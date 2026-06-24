#include <pthread.h>
#include <semaphore.h>

typedef struct {
	pthread_mutex_t pmutex;
} my_mutex_t;

extern int my_mutex_init(my_mutex_t *mutex);
extern int my_mutex_lock(my_mutex_t *mutex);
extern int my_mutex_unlock(my_mutex_t *mutex);
extern int my_mutex_destroy(my_mutex_t *mutex);

typedef struct {
	sem_t psem;
} my_sem_t;

extern int my_sem_init(my_sem_t *sem);
extern int my_sem_wait(my_sem_t *sem);
extern int my_sem_post(my_sem_t *sem);
extern int my_sem_destroy(my_sem_t *sem);

typedef struct {
	int *buffer;
	int capacity;
	int head;
	int tail;
	int count;
	pthread_mutex_t lock;
	pthread_cond_t not_empty;
	pthread_cond_t not_full;
} my_msgq_t;

extern int my_msgq_init(my_msgq_t *mq, int capacity);
extern int my_msgq_send(my_msgq_t *mq, int msg);
extern int my_msgq_receive(my_msgq_t *mq, int *msg);
extern int my_msgq_destroy(my_msgq_t *mq);
