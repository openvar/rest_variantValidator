from locust import HttpUser, TaskSet, task, between
import test_set


class UserBehavior(TaskSet):

    @task(2)
    def gene2transcripts_v2_task(self):
        gene_symbol = test_set.gene_list()
        url = f"/VariantValidator/tools/gene2transcripts_v2/{gene_symbol}/mane/all/GRCh38?content-type=application%2Fjson"
        self.client.get(url, timeout=300)

    @task(1)
    def variantvalidator_task(self):
        variant_id = test_set.variant_list()
        url = f"/VariantValidator/variantvalidator/GRCh37/{variant_id}/mane?content-type=application/json"
        self.client.get(url, timeout=300)

    @task(3)
    def lovd_task_grch38(self):
        odd_task = test_set.vf_list()
        url = f"/LOVD/lovd/GRCh38/{odd_task}/all/all/False/True?content-type=application%2Fjson"
        self.client.get(url, timeout=300)

    @task(4)
    def lovd_task_grch37(self):
        odd_task = test_set.vf_list()
        url = f"/LOVD/lovd/GRCh37/{odd_task}/all/all/False/True?content-type=application%2Fjson"
        self.client.get(url, timeout=300)


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(0.1, 0.3)  # roughly 3-4 requests/sec per user

# <LICENSE>
# Copyright (C) 2016-2026 VariantValidator Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# </LICENSE>