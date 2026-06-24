#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "bank_op_verify.h"

pthread_mutex_t v_mutex;
int v_account_balance = 10000;

void v_init(int balance)
{
	pthread_mutex_init(&v_mutex, NULL);
	v_account_balance = balance;
}

void v_account_op(int amount)
{
	pthread_mutex_lock(&v_mutex);
	/* vvv critical reagion vvv */

	int balance = v_account_balance;
	int balance_new = balance + amount;

	if (balance_new >= 0)
		v_account_balance = balance_new;

	/* ^^^ critical reagion ^^^*/
	pthread_mutex_unlock(&v_mutex);
}

int v_fin(void)
{
	pthread_mutex_destroy(&v_mutex);
	return v_account_balance;
}
