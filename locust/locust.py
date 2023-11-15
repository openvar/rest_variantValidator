from locust import HttpUser, TaskSet, task, between
import test_set


class UserBehavior(TaskSet):
    @task(2, max_wait=300)
    def gene2transcripts_v2_task(self):
        gene_symbol = test_set.gene_list()
        url = f"https://rest.variantvalidator.org/VariantValidator/tools/gene2transcripts_v2/{gene_symbol}/mane_select/all/GRCh38?content-type=application%2Fjson"
        self.client.get(url)

    @task(1, max_wait=300)
    def variantvalidator_task(self):
        variant_id = test_set.variant_list()
        url = f"/VariantValidator/variantvalidator/GRCh37/{variant_id}/all?content-type=application/json"
        self.client.get(url)

    @task(3, max_wait=300)
    def additional_task(self):
        odd_task = test_set.vf_list()
        url = f"https://rest.variantvalidator.org/LOVD/lovd/GRCh38/{odd_task}/all/all/False/True?content-type=application%2Fjson"
        self.client.get(url)


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 10)  # seconds

# <LICENSE>
# Copyright (C) 2016-2023 VariantValidator Contributors
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
