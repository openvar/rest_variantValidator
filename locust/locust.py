from locust import HttpUser, TaskSet, task, between
import test_set


class UserBehavior(TaskSet):
    @task(2)
    def gene2transcripts_v2_task(self):
        gene_symbol = test_set.gene_list()
        url = f"https://rest.variantvalidator.org/VariantValidator/tools/gene2transcripts_v2/{gene_symbol}/mane_select/all/GRCh38?content-type=application%2Fjson"
        self.client.get(url)

    @task(1)
    def variantvalidator_task(self):
        variant_id = test_set.variant_list()
        url = f"/VariantValidator/variantvalidator/GRCh37/{variant_id}/all?content-type=application/json"
        self.client.get(url)
        # Simulate a long response time (5 minutes)
        self.wait(300)

    @task(3)
    def additional_task(self):
        odd_task = test_set.vf_list()
        url = f"https://rest.variantvalidator.org/LOVD/lovd/GRCh38/{odd_task}/all/all/False/True?content-type=application%2Fjson"
        self.client.get(url)
        # Simulate a long response time (5 minutes)
        self.wait(300)


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 10)  # seconds
