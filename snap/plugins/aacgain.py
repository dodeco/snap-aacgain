from snapcraft import BasePlugin
from snapcraft.file_utils import link_or_copy
from snapcraft.sources import Git, Tar, Zip
import os
import shutil

class AacGain(BasePlugin):
    def __init__(self, name, options, project):
        super().__init__(name, options, project)

        self._aacgain_build_dir = os.path.join(self.builddir, "aacgain")
        self._aacgain_source = Git("git://git.code.sf.net/p/mp3gain/code", self.sourcedir, source_tag="R1_9")

        self._faad2_build_dir = os.path.join(self.builddir, "faad2")
        self._faad2_source_dir = os.path.join(self.sourcedir, "faad2")
        self._faad2_source = Tar("https://downloads.sourceforge.net/project/faac/faad2-src/faad2-2.7/faad2-2.7.tar.bz2", self._faad2_source_dir)

        self._mp3gain_build_dir = os.path.join(self.builddir, "mp3gain")
        self._mp3gain_source_dir = os.path.join(self.sourcedir, "mp3gain")
        self._mp3gain_source = Zip("https://downloads.sourceforge.net/project/mp3gain/mp3gain/1.5.1/mp3gain-1_5_1-src.zip", self._mp3gain_source_dir)

        self._mp4v2_build_dir = os.path.join(self.builddir, "mp4v2")
        self._mp4v2_source_dir = os.path.join(self.sourcedir, "mp4v2")
        self._mp4v2_source = Tar("https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/mp4v2/mp4v2-trunk-r355.tar.bz2", self._mp4v2_source_dir)

    def pull(self):
        shutil.rmtree(self.sourcedir)
        self._aacgain_source.pull()

        os.makedirs(self._faad2_source_dir, exist_ok=True)
        self._faad2_source.pull()

        os.makedirs(self._mp3gain_source_dir, exist_ok=True)
        self._mp3gain_source.pull()

        os.makedirs(self._mp4v2_source_dir, exist_ok=True)
        self._mp4v2_source.pull()

    def build(self):
        self.run(["patch", "-p2", "-N", "-i", os.path.join(self._aacgain_build_dir, "mp4v2.patch")], self._mp4v2_build_dir)
        self.run(["./configure", "CXXFLAGS=-fpermissive"], self._mp4v2_build_dir)
        self.run(["make", "-j{}".format(self.parallel_build_count), "libmp4v2.la"], self._mp4v2_build_dir)

        self.run(["./configure"], self._faad2_build_dir)
        self.run(["make", "-j{}".format(self.parallel_build_count)], os.path.join(self._faad2_build_dir, "libfaad"))

        aacgain_linux_dir = os.path.join(self._aacgain_build_dir, "linux")
        self.run(["patch", "-p3", "-N", "-i", os.path.join(aacgain_linux_dir, "mp3gain.patch")], self._mp3gain_build_dir)
        self.run(["sed", "-i", "/^patch/d", "prepare.sh"], aacgain_linux_dir)
        self.run(["chmod", "+x", "prepare.sh"], aacgain_linux_dir)
        self.run(["./prepare.sh"], aacgain_linux_dir)

        aacgain_build_dir = os.path.join(aacgain_linux_dir, "build")
        os.makedirs(aacgain_build_dir, exist_ok=True)
        self.run(["{}/configure".format(self.builddir)], aacgain_build_dir)
        self.run(["make"], aacgain_build_dir)

        link_or_copy(os.path.join(aacgain_build_dir, "aacgain", "aacgain"), os.path.join(self.installdir, "aacgain"))
