from locust import HttpUser, TaskSet, task, between
import test_set
import json

# -----------------------------------------------------
# User behavior tasks
# -----------------------------------------------------
class UserBehavior(TaskSet):

    @task(1)
    def gene2transcripts_v2_task(self):
        gene_symbol = test_set.gene_list()
        payload = {
            "gene_query": gene_symbol,
            "genome_build": "GRCh38",
            "transcript_set": "all",
            "limit_transcripts": "mane_select",
            "show_exon_info": False
        }
        # Allow up to 5 minutes for response
        self.client.post("/tools/gene2transcripts_v2", json=payload, timeout=300)

    @task(2)
    def variantvalidator_task(self):
        variant_id = test_set.variant_list()
        payload = {
            "variant_description": variant_id,
            "genome_build": "GRCh37",
            "select_transcripts": "mane_select",
            "transcript_model": "refseq"
        }
        self.client.post("/VariantValidator", json=payload, timeout=300)

    @task(3)
    def variantformatter_task(self):
        vf_variant = test_set.vf_list()
        payload = [
            {
                "variant_description": vf_variant,
                "genome_build": "GRCh38",
                "transcript_model": "refseq",
                "select_transcripts": "all",
                "checkonly": False,
                "liftover": False
            }
        ]
        self.client.post("/VariantFormatter_v2", json=payload, timeout=300)

    @task(4)
    def variantformatter_task(self):
        vf_variant = test_set.vf_list()
        payload = [
            {
                "variant_description": vf_variant,
                "genome_build": "GRCh37",
                "transcript_model": "refseq",
                "select_transcripts": "all",
                "checkonly": False,
                "liftover": False
            }
        ]
        self.client.post("/VariantFormatter_v2", json=payload, timeout=300)

    @task(5)
    def variantvalidator_task(self):
        variant_id = test_set.variant_list()
        payload = {
            "variant_description": variant_id,
            "genome_build": "GRCh38",
            "select_transcripts": "mane_select",
            "transcript_model": "refseq"
        }
        self.client.post("/VariantValidator", json=payload, timeout=300)


# -----------------------------------------------------
# Main user definition
# -----------------------------------------------------
class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(0.1, 0.3)  # roughly 3-4 requests/sec per user