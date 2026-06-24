#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <pthread.h>

#include "bank_op_verify.h"
#include "my_sync.h"

#define NUM_OPS_PER_THREAD 10000
#define NUM_THREADS 2
#define MQ_CAPACITY 256
#define MQ_TERMINATE INT_MAX
#define DEBUG 0

int account_balance = 10000;
my_mutex_t account_mutex;
my_sem_t account_sem;
my_msgq_t account_mq;
pthread_t mq_thread;

enum sync_mode {
	SYNC_NONE,
	SYNC_MUTEX,
	SYNC_SEM,
	SYNC_MQ,
};

static enum sync_mode mode = SYNC_NONE;

static void apply_amount(int amount)
{
	int balance = account_balance;
	int balance_new = balance + amount;

	if (balance_new >= 0) {
#if DEBUG
		printf("%d%+d=%d\n", balance, amount, balance_new);
#endif
		account_balance = balance_new;
	}
}

static void account_op_mutex(int amount)
{
	my_mutex_lock(&account_mutex);
	apply_amount(amount);
	my_mutex_unlock(&account_mutex);
}

static void account_op_sem(int amount)
{
	my_sem_wait(&account_sem);
	apply_amount(amount);
	my_sem_post(&account_sem);
}

static void account_op_mq(int amount)
{
	my_msgq_send(&account_mq, amount);
}

void account_op(int amount)
{
	switch (mode) {
	case SYNC_MUTEX:
		account_op_mutex(amount);
		break;
	case SYNC_SEM:
		account_op_sem(amount);
		break;
	case SYNC_MQ:
		account_op_mq(amount);
		break;
	default:
		apply_amount(amount);
	}
}

static void *mq_processor(void *ptr)
{
	int amount;

	while (1) {
		my_msgq_receive(&account_mq, &amount);
		if (amount == MQ_TERMINATE)
			break;
		apply_amount(amount);
	}

	return NULL;
}

static int init_sync(void)
{
	int ret = 0;

	switch (mode) {
	case SYNC_MUTEX:
		ret = my_mutex_init(&account_mutex);
		break;
	case SYNC_SEM:
		ret = my_sem_init(&account_sem);
		break;
	case SYNC_MQ:
		ret = my_msgq_init(&account_mq, MQ_CAPACITY);
		if (ret == 0)
			ret = pthread_create(&mq_thread, NULL, mq_processor, NULL);
		break;
	default:
		break;
	}

	return ret;
}

static void destroy_sync(void)
{
	switch (mode) {
	case SYNC_MUTEX:
		my_mutex_destroy(&account_mutex);
		break;
	case SYNC_SEM:
		my_sem_destroy(&account_sem);
		break;
	case SYNC_MQ:
		my_msgq_send(&account_mq, MQ_TERMINATE);
		pthread_join(mq_thread, NULL);
		my_msgq_destroy(&account_mq);
		break;
	default:
		break;
	}
}

static void print_usage(const char *progname)
{
	printf("Usage: %s [mutex|sem|mq]\n", progname);
}

void *work_thread(void *ptr)
{
	int amount;

	for (int i = 0; i < NUM_OPS_PER_THREAD; i++) {
		amount = random() % 2000 - 1000;
		account_op(amount);
		v_account_op(amount);
	}

	return NULL;
}

int main(int argc, char **argv)
{
	pthread_t thread[NUM_THREADS];

	if (argc != 2) {
		print_usage(argv[0]);
		return 1;
	}

	if (strcmp(argv[1], "mutex") == 0) {
		mode = SYNC_MUTEX;
	} else if (strcmp(argv[1], "sem") == 0) {
		mode = SYNC_SEM;
	} else if (strcmp(argv[1], "mq") == 0) {
		mode = SYNC_MQ;
	} else {
		print_usage(argv[0]);
		return 1;
	}

	srandom(time(NULL));
	v_init(account_balance);

	if (init_sync() != 0) {
		fprintf(stderr, "Failed to initialize synchronization mechanism\n");
		return 1;
	}

	for (int i = 0; i < NUM_THREADS; i++) {
		pthread_create(&thread[i], NULL, work_thread, NULL);
	}

	for (int i = 0; i < NUM_THREADS; i++) {
		pthread_join(thread[i], NULL);
	}

	destroy_sync();

	printf("Processed balance : %d\n", account_balance);
	int correct_balance = v_fin();
	printf("Correct balance : %d\n", correct_balance);

	return 0;
}
