import atexit
import datetime
import faulthandler
import os
import tempfile
import unittest

import numpy as np

faulthandler.enable()  # to debug seg faults and timeouts

import cf

n_tmpfiles = 1
tmpfiles = [
    tempfile.mkstemp("_test_pp.nc", dir=os.getcwd())[1]
    for i in range(n_tmpfiles)
]
[tmpfile] = tmpfiles


def _remove_tmpfiles():
    """Try to remove defined temporary files by deleting their paths."""
    for f in tmpfiles:
        try:
            os.remove(f)
        except OSError:
            pass


atexit.register(_remove_tmpfiles)


class ppTest(unittest.TestCase):
    ppfile = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "wgdos_packed.pp"
    )

    ppextradata = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "extra_data.pp"
    )

    new_table = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "new_STASH_to_CF.txt"
    )
    text_file = open(new_table, "w")
    text_file.write(
        "1!30201!long name                           !Pa!!!NEW_NAME!!"
    )
    text_file.close()

    chunk_sizes = (800000, 80000)

    def test_load_stash2standard_name(self):
        f = cf.read(self.ppfile)[0]
        self.assertEqual(f.identity(), "eastward_wind")
        self.assertEqual(f.Units, cf.Units("m s-1"))

        for merge in (True, False):
            cf.load_stash2standard_name(self.new_table, merge=merge)
            f = cf.read(self.ppfile)[0]
            self.assertEqual(f.identity(), "NEW_NAME")
            self.assertEqual(f.Units, cf.Units("Pa"))
            cf.load_stash2standard_name()
            f = cf.read(self.ppfile)[0]
            self.assertEqual(f.identity(), "eastward_wind")
            self.assertEqual(f.Units, cf.Units("m s-1"))

        cf.load_stash2standard_name()

    def test_stash2standard_name(self):
        d = cf.stash2standard_name()
        self.assertIsInstance(d, dict)
        d["test"] = None
        e = cf.stash2standard_name()
        self.assertNotEqual(d, e)

    def test_PP_read_select(self):
        f = cf.read(self.ppfile, select="lbproc=0")
        self.assertEqual(len(f), 1)

    def test_PP_WGDOS_UNPACKING(self):
        f = cf.read(self.ppfile)[0]

        self.assertEqual(f.data.mean(), 3.8080420658506196)

        array = f.array

        for chunksize in self.chunk_sizes:
            with cf.CHUNKSIZE(chunksize):
                f = cf.read(self.ppfile)[0]

                for fmt in ("NETCDF4", "CFA4"):
                    cf.write(f, tmpfile, fmt=fmt)
                    g = cf.read(tmpfile)[0]

                    self.assertTrue(
                        (f.array == array).all(),
                        "Bad unpacking of PP WGDOS packed data",
                    )

                    self.assertTrue(
                        f.equals(g, verbose=2),
                        "Bad writing/reading. fmt=" + fmt,
                    )

    def test_PP_extra_data(self):
        f = cf.read(self.ppextradata)[0]

        self.assertEqual(len(f.dimension_coordinates()), 3)
        self.assertEqual(len(f.auxiliary_coordinates()), 3)

        sites = f.dimension_coordinate("long_name=site")
        self.assertTrue(np.allclose(sites, [1, 2, 3]))

        regions = f.auxiliary_coordinate("region").array
        self.assertTrue(
            regions.tolist()
            == ["Northern Hemisphere", "Southern Hemisphere", "Global"]
        )

        self.assertTrue(f.dimension_coordinate("height", default=False))
        self.assertTrue(f.dimension_coordinate("time", default=False))
        self.assertTrue(f.auxiliary_coordinate("longitude", default=False))
        self.assertTrue(f.auxiliary_coordinate("longitude", default=False))


if __name__ == "__main__":
    print("Run date:", datetime.datetime.now())
    cf.environment()
    print()
    unittest.main(verbosity=2)
