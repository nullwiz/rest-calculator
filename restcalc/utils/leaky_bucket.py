from restcalculator.uow_factory import create_cache_uow
from restcalculator.exceptions.custom_exceptions import TaskNotFoundException
import time
import json
from datetime import datetime


class UserCacheHandler():
    """
    Handles cache for a given user. Built-in leaky bucket. 
    """

    def __init__(self, user_id) -> None:
        self.user_id = user_id
        self.MAX_ALLOWED_TOKENS = 6
        self.REFILL_RATE = 10  # 10 seconds
        with create_cache_uow() as uow:
            user = uow.get(self.user_id)
            if user is None:
                user_data = {
                    "tokens": self.MAX_ALLOWED_TOKENS,
                    "last_refill_time": time.time(),
                    "tasks": {},
                    "updated_at": time.time()
                }
                uow.set(self.user_id, json.dumps(user_data))
            else:
                pass

    def block_or_not(self):
        """
        Returns True if the user should be blocked, False otherwise.
        Creates the user key if not present in redis.
        """
        with create_cache_uow() as uow:
            while True:
                try:
                    # Start watching the user key for changes
                    uow.watch(self.user_id)

                    user = json.loads(uow.get(self.user_id))
                    print(user)
                    now = time.time()
                    time_since_last_refill = now - user["last_refill_time"]
                    tokens_to_refill = int(
                        time_since_last_refill / self.REFILL_RATE)
                    if tokens_to_refill >= 0:
                        user["tokens"] = min(
                            user["tokens"] + tokens_to_refill, self.MAX_ALLOWED_TOKENS)
                        user["last_refill_time"] = now
                    if user["tokens"] == 0:
                        return False

                    user["tokens"] -= 1

                    # Start a transaction
                    pipe = uow.client.pipeline()
                    pipe.multi()
                    pipe.set(self.user_id, json.dumps(user))
                    pipe.execute()

                    return True
                except uow.WatchError:
                    # If the key changed before the transaction was executed, retry the loop
                    continue

    def add_new_task(self, task_id, total_rows=0):
        with create_cache_uow() as uow:
            while True:
                try:
                    uow.watch(self.user_id)

                    user = json.loads(uow.get(self.user_id))
                    task_data = {
                        "status": "pending",
                        "updated_at": time.time(),
                        "created_at": time.time(),
                        "percentage": 0,
                        "lines": 0,
                        "total_lines": total_rows,
                    }
                    user["tasks"][task_id] = task_data

                    pipe = uow.client.pipeline()
                    pipe.multi()
                    pipe.set(self.user_id, json.dumps(user))
                    pipe.execute()

                    break
                except uow.WatchError:
                    continue

    def update_task(self, task_id, status):
        """
        task_id : str, id to be updated
        status: can be either pending, processing, done, or error
        """
        with create_cache_uow() as uow:
            while True:
                try:
                    uow.watch(self.user_id)
                    user = json.loads(uow.get(self.user_id))
                    task = user["tasks"][task_id]
                    print("USERRRRRRRRRRRRR")
                    print(user)
                    print(task)
                    if task is None:
                        raise TaskNotFoundException("Task not found")
                    else:
                        task["status"] = status
                        task["updated_at"] = time.time()

                    pipe = uow.client.pipeline()
                    pipe.multi()
                    pipe.set(self.user_id, json.dumps(user))
                    pipe.execute()

                    break
                except uow.WatchError:
                    continue

    def update_progress(self, task_id, percentage, lines, total_lines=None):
        """
        task_id : str, id to be updated
        percentage: int, percentage of completion
        line: int, last line being processed
        """
        with create_cache_uow() as uow:
            while True:
                try:
                    uow.watch(self.user_id)
                    user = json.loads(uow.get(self.user_id))
                    task = user["tasks"][task_id]
                    if task is None:
                        raise TaskNotFoundException("Task not found")
                    else:
                        print("task is here")
                        print(task)
                        task["percentage"] = percentage
                        task["updated_at"] = time.time()
                        if total_lines:
                            task["total_lines"] = total_lines
                    pipe = uow.client.pipeline()
                    pipe.multi()
                    pipe.set(self.user_id, json.dumps(user))
                    pipe.execute()

                    break
                except uow.WatchError:
                    continue

    def get_task(self, task_id):
        with create_cache_uow() as uow:
            user = json.loads(uow.get(self.user_id))
            try:
                task = user["tasks"][task_id]
            except KeyError:
                return None
            return task

    def update_error(self, task_id, error, line=0):
        with create_cache_uow() as uow:
            while True:
                try:
                    uow.watch(self.user_id)
                    user = json.loads(uow.get(self.user_id))
                    task = user["tasks"][task_id]
                    if task is None:
                        raise TaskNotFoundException("Task not found")
                    else:
                        task["error"] = error
                        task["line"] = line
                        task["status"] = "error"
                        task["updated_at"] = time.time()
                    pipe = uow.client.pipeline()
                    pipe.multi()
                    pipe.set(self.user_id, json.dumps(user))
                    pipe.execute()

                    break
                except uow.WatchError:
                    continue

    def get_lines_processed(self, task_id):
        with create_cache_uow() as uow:
            user = json.loads(uow.get(self.user_id))
            task = user["tasks"][task_id]
            return task["lines"]
