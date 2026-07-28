#! /usr/bin/env python
# Copyright (c) 2026 TOYOTA MOTOR CORPORATION
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted (subject to the limitations in the disclaimer
# below) provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the copyright holder nor the names of its contributors may be used
#   to endorse or promote products derived from this software without specific
#   prior written permission.
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS
# LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.
# -*- coding: utf-8 -*-
"""

@author: Keisuke Takeshita
"""
import unittest

import actionlib

from actionlib_msgs.msg import GoalStatus
import rospy
from std_msgs.msg import String

from tmc_msgs.msg import (
    TalkRequestAction,
    TalkRequestActionFeedback,
    TalkRequestGoal,
    Voice,
)


def create_talk_request(sentence, lauguage):
    goal = TalkRequestGoal()
    goal.data.interrupting = False
    goal.data.queueing = True
    goal.data.language = lauguage
    goal.data.sentence = sentence
    return goal


class TestTalkRequestAction(unittest.TestCase):
    def setUp(self):
        self._client = actionlib.SimpleActionClient(
            "/talk_request_action", TalkRequestAction)
        self._client.wait_for_server()

        self._publisher = rospy.Publisher("/talk_request", Voice,
                                          queue_size=10)
        rate = rospy.Rate(10.0)
        while (self._publisher.get_num_connections() == 0):
            rate.sleep()

        self._sentences = []
        self._subscriber = rospy.Subscriber(
            '/talking_sentence', String, self._sentence_callback,
            queue_size=10)
        # /talking_sentences is latched, the value of the previous test is included in the 0th element, so it is removed
        while len(self._sentences) == 0:
            rate.sleep()
        self._sentences = []

    def _sentence_callback(self, msg):
        self._sentences.append((rospy.Time.now().to_sec(), msg.data))

    def test_valid_language(self):
        u"""Does it work with supported languages?"""
        result = self._client.send_goal_and_wait(
            create_talk_request(u"A", Voice.kJapanese))
        self.assertEqual(result, GoalStatus.SUCCEEDED)

        result = self._client.send_goal_and_wait(
            create_talk_request("a", Voice.kEnglish))
        self.assertEqual(result, GoalStatus.SUCCEEDED)

        # Originally, it should receive an empty message when send_goal_and_wait is completed
        # However, due to timing issues, it is not guaranteed to receive it, so check if the size is 3 or more
        self.assertGreaterEqual(len(self._sentences), 3)
        self.assertEqual(self._sentences[0][1], "A")
        self.assertEqual(self._sentences[1][1], "")
        self.assertEqual(self._sentences[2][1], "a")

    def test_invalid_language(self):
        u"""Does it work with unsupported languages?"""
        result = self._client.send_goal_and_wait(
            create_talk_request("hoge", 42))
        self.assertEqual(result, GoalStatus.ABORTED)
        self.assertEqual(len(self._sentences), 0)

    def test_send_action_in_topic(self):
        u"""Can an action interrupt playback by a topic?"""
        self._publisher.publish(
            create_talk_request("01234", Voice.kEnglish).data)
        rospy.sleep(0.2)

        result = self._client.send_goal_and_wait(
            create_talk_request("43210", Voice.kEnglish))
        self.assertEqual(GoalStatus.SUCCEEDED, result)

        self.assertGreaterEqual(len(self._sentences), 2)
        time_diff = self._sentences[1][0] - self._sentences[0][0]
        self.assertAlmostEqual(time_diff, 0.2, delta=0.1)
        self.assertEqual(self._sentences[0][1], "01234")
        self.assertEqual(self._sentences[1][1], "43210")

    def test_send_topic_in_action(self):
        u"""Can a topic interrupt playback by an action?"""
        self._client.send_goal(
            create_talk_request("01234", Voice.kEnglish))
        rospy.sleep(0.2)

        self._publisher.publish(
            create_talk_request("43210", Voice.kEnglish).data)
        rospy.sleep(1.0)

        self.assertEqual(self._client.get_state(), GoalStatus.PREEMPTED)
        self.assertEqual(len(self._sentences), 3)
        time_diff = self._sentences[1][0] - self._sentences[0][0]
        self.assertAlmostEqual(time_diff, 0.2, delta=0.1)
        self.assertEqual(self._sentences[0][1], "01234")
        self.assertEqual(self._sentences[1][1], "43210")
        self.assertEqual(self._sentences[2][1], "")

    def test_send_topic_in_topic(self):
        u"""Can a topic interrupt playback by another topic?"""
        self._publisher.publish(
            create_talk_request("01234", Voice.kEnglish).data)
        rospy.sleep(0.2)

        self._publisher.publish(
            create_talk_request("43210", Voice.kEnglish).data)
        rospy.sleep(1.0)

        self.assertEqual(len(self._sentences), 3)
        time_diff = self._sentences[1][0] - self._sentences[0][0]
        self.assertAlmostEqual(time_diff, 0.2, delta=0.1)
        self.assertEqual(self._sentences[0][1], "01234")
        self.assertEqual(self._sentences[1][1], "43210")
        self.assertEqual(self._sentences[2][1], "")

    def test_send_action_in_action(self):
        u"""Can an action interrupt playback by another action?"""
        self._client.send_goal(
            create_talk_request("01234", Voice.kEnglish))
        rospy.sleep(0.2)

        result = self._client.send_goal_and_wait(
            create_talk_request("43210", Voice.kEnglish))
        self.assertEqual(GoalStatus.SUCCEEDED, result)

        self.assertGreaterEqual(len(self._sentences), 2)
        time_diff = self._sentences[1][0] - self._sentences[0][0]
        self.assertAlmostEqual(time_diff, 0.2, delta=0.1)
        self.assertEqual(self._sentences[0][1], "01234")
        self.assertEqual(self._sentences[1][1], "43210")

    def test_cancel_action(self):
        u"""Can playback by an action be canceled?"""
        self._client.send_goal(
            create_talk_request("01234", Voice.kEnglish))
        rospy.sleep(0.2)

        self._client.cancel_goal()
        self.assertTrue(self._client.wait_for_result())
        self.assertEqual(GoalStatus.PREEMPTED, self._client.get_state())

    def test_cancel_topic(self):
        u"""Can playback by a topic be canceled?"""
        self._publisher.publish(
            create_talk_request("01234", Voice.kEnglish).data)
        rospy.sleep(0.2)

        self._client.cancel_goal()
        rospy.sleep(0.5)

        # Since it cannot be canceled, an empty string should be issued after 0.5 seconds
        self.assertGreaterEqual(len(self._sentences), 2)
        time_diff = self._sentences[1][0] - self._sentences[0][0]
        self.assertAlmostEqual(time_diff, 0.5, delta=0.1)
        self.assertEqual(self._sentences[0][1], "01234")
        self.assertEqual(self._sentences[1][1], "")

    def test_action_feedback(self):
        u"""Does the feedback of the action monotonically decrease?"""
        self._feedbacks = []
        feedback_sub = rospy.Subscriber(
            "/talk_request_action/feedback",
            TalkRequestActionFeedback,
            callback=self._feedback_callback)
        rate = rospy.Rate(10.0)
        while (feedback_sub.get_num_connections() == 0):
            rate.sleep()

        self._client.send_goal_and_wait(
            create_talk_request("0123456789", Voice.kEnglish))
        self.assertAlmostEqual(1.0, self._feedbacks[0].to_sec(), delta=0.2)
        self.assertAlmostEqual(0.0, self._feedbacks[-1].to_sec(), delta=0.2)
        for index in range(1, len(self._feedbacks)):
            self.assertGreater(self._feedbacks[index - 1].to_sec(),
                               self._feedbacks[index].to_sec())

    def _feedback_callback(self, msg):
        self._feedbacks.append(msg.feedback.remaining_time)


if __name__ == '__main__':
    rospy.init_node('test_talk_request_action')
    import rostest
    rostest.rosrun('tmc_talk_hoya_py',
                   'test_talk_request_action',
                   TestTalkRequestAction)
