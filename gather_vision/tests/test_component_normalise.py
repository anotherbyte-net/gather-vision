from django.test import TestCase

from gather_vision.process.component.normalise import Normalise


class TestPlaylistsComponentNormalise(TestCase):
    def test_tracks(self):
        n = Normalise()

        tricky = [
            (
                ("Intimidated (feat. H.E.R.)", ["KAYTRANADA"], "H.E.R."),
                ("intimidated", ["kaytranada"], ["h.e.r."]),
            ),
            (
                ("Call My Name (feat. Robyn)", ["Smile"], ["Robyn"]),
                ("call my name", ["smile"], ["robyn"]),
            ),
            (
                ("Kiss Of Life", "Kylie Minogue & Jessie Ware", []),
                ("kiss of life", ["kylie minogue"], ["jessie ware"]),
            ),
        ]

        for (in_t, in_p, in_f), (exp_t, exp_p, exp_f) in tricky:
            with self.subTest(
                in_t=in_t, in_p=in_p, in_f=in_f, exp_t=exp_t, exp_p=exp_p, exp_f=exp_f
            ):
                act_t, act_p, act_f, act_q = n.track(in_t, in_p, in_f)
                self.assertEqual(act_t, exp_t)
                self.assertEqual(act_p, exp_p)
                self.assertEqual(act_f, exp_f)
