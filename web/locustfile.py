from random import randint
from locust import HttpUser, task, between
from locust.user import wait_time

class StressTest(HttpUser):
    wait_time = between(60,70)

    @task
    def get_banner(self):
        i = randint(1,50)
        self.client.get(f"/campaigns/{i}")
