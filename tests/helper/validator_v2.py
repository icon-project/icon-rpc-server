# Copyright 2017 theloop Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def validate_block(self, block):
    self.assertIn('version', block)

    int(block['prev_block_hash'], 16)
    self.assertEqual(len(block['prev_block_hash']), 64)

    int(block['merkle_tree_root_hash'], 16)
    self.assertEqual(len(block['merkle_tree_root_hash']), 64)

    int(block['block_hash'], 16)
    self.assertEqual(len(block['block_hash']), 64)

    # int(block['height'])

    self.assertIn('peer_id', block)
    self.assertIn('signature', block)

    # int(block['time_stamp'])
