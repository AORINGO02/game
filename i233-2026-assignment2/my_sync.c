#include <stdlib.h>
#include "my_sync.h"

int my_mutex_init(my_mutex_t *mutex)
{
	return pthread_mutex_init(&mutex->pmutex, NULL);
}

int my_mutex_lock(my_mutex_t *mutex)
{
	return pthread_mutex_lock(&mutex->pmutex);
}

int my_mutex_unlock(my_mutex_t *mutex)
{
	return pthread_mutex_unlock(&mutex->pmutex);
}

int my_mutex_destroy(my_mutex_t *mutex)
{
	return pthread_mutex_destroy(&mutex->pmutex);
}

int my_sem_init(my_sem_t *sem)
{
	return sem_init(&sem->psem, 0, 1);
}

int my_sem_wait(my_sem_t *sem)
{
	return sem_wait(&sem->psem);
}

int my_sem_post(my_sem_t *sem)
{
	return sem_post(&sem->psem);
}

int my_sem_destroy(my_sem_t *sem)
{
	return sem_destroy(&sem->psem);
}

int my_msgq_init(my_msgq_t *mq, int capacity)
{
	if (capacity <= 0)
		return -1;

	mq->buffer = malloc(sizeof(int) * capacity);
	if (mq->buffer == NULL)
		return -1;

	mq->capacity = capacity;
	mq->head = mq->tail = mq->count = 0;
	pthread_mutex_init(&mq->lock, NULL);
	pthread_cond_init(&mq->not_empty, NULL);
	pthread_cond_init(&mq->not_full, NULL);

	return 0;
}

int my_msgq_send(my_msgq_t *mq, int msg)
{
	pthread_mutex_lock(&mq->lock);
	while (mq->count == mq->capacity)
		pthread_cond_wait(&mq->not_full, &mq->lock);

	mq->buffer[mq->tail] = msg;
	mq->tail = (mq->tail + 1) % mq->capacity;
	mq->count++;
	pthread_cond_signal(&mq->not_empty);
	pthread_mutex_unlock(&mq->lock);

	return 0;
}

int my_msgq_receive(my_msgq_t *mq, int *msg)
{
	pthread_mutex_lock(&mq->lock);
	while (mq->count == 0)
		pthread_cond_wait(&mq->not_empty, &mq->lock);

	*msg = mq->buffer[mq->head];
	mq->head = (mq->head + 1) % mq->capacity;
	mq->count--;
	pthread_cond_signal(&mq->not_full);
	pthread_mutex_unlock(&mq->lock);

	return 0;
}

int my_msgq_destroy(my_msgq_t *mq)
{
	pthread_mutex_destroy(&mq->lock);
	pthread_cond_destroy(&mq->not_empty);
	pthread_cond_destroy(&mq->not_full);
	free(mq->buffer);
	return 0;
}
