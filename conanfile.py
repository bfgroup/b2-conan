'''
@author: René Ferdinand Rivera Morell
@copyright: Copyright René Ferdinand Rivera Morell 2022
@license:
    Distributed under the Boost Software License, Version 1.0.
    (See accompanying file LICENSE_1_0.txt or copy at
    http://www.boost.org/LICENSE_1_0.txt)
'''
from conan import ConanFile, tools
import os

required_conan_version = ">=1.53.0"


class Package(ConanFile):
    name = "b2-conan"
    version = "1.0.3"
    homepage = "https://github.com/bfgroup/b2-conan"
    description = "Build utility tool to invoke b2 for building packages."
    topics = ("b2", "tool", "build")
    license = "BSL-1.0"
    url = "https://github.com/bfgroup/b2-conan"
    barbarian = {
        "description": {
            "format": "asciidoc",
            "file": "README.adoc"
        }
    }
    exports = ("README.adoc", "LICENSE.txt")
    settings = []
    no_copy_source = True


class B2():

    def __init__(self, conanfile):
        self.conanfile = conanfile
        self.flags = []
        for name in dir(self):
            if name.startswith('_add_flags_'):
                getattr(self, name)()

    def build(self, args=None, build_dir=None, target=None):
        '''
        Invoke b2 to build the default, or given target.
        * args (Optional, Defaulted to `None`) Extra arguments to invoke B2
          with.
        * build_dir (Optional, Defaulted to `None`) The intermediate output
          build directory.
        * target (Optional, Defaulted to `None`) A set of one or more targets
          to build. These are added to the command line invocation directly.
          And must use the B2 target syntax.
        '''
        if not self.conanfile.should_build:
            return
        command = ["b2"]
        if args:
            command.extend(args)
        if build_dir:
            command.append('--build-dir="%"' % (build_dir))
        command.extend(self.flags)
        if target:
            if isinstance(target, str):
                command.append(target)
            else:
                command.extend(target)
        self.conanfile.output.info('"{}"'.format('" "'.join(command)))
        return self.conanfile.run(command, run_environment=True)

    @property
    def toolset(self):
        return {
            'apple-clang': 'clang',
            'clang': 'clang',
            'gcc': 'gcc',
            'sun-cc': 'sun',
            'Visual Studio': 'msvc',
            'msvc': 'msvc'
        }.get(self.conanfile.settings.get_safe('compiler'))+'-'+self.toolset_version

    @property
    def toolset_version(self):
        if self.conanfile.settings.compiler == 'Visual Studio':
            return {
                "8": "8.0",
                "9": "9.0",
                "10": "10.0",
                "11": "11.0",
                "12": "12.0",
                "14": "14.0",
                "15": "14.1",
                "16": "14.2",
                "17": "14.3",
            }.get(str(self.conanfile.settings.compiler.version))
        if self.conanfile.settings.compiler == 'msvc':
            msvc_version = self.conanfile.settings.compiler.version
            return {
                "140": "8.0",
                "150": "9.0",
                "160": "10.0",
                "170": "11.0",
                "180": "12.0",
                "190": "14.0",
                "191": "14.1",
                "192": "14.2",
                "193": "14.3",
            }.get('{}'.format(msvc_version))
        if self.conanfile.settings.compiler == 'apple-clang':
            return str(self.conanfile.settings.compiler.version).split('.')[0]
        return str(self.conanfile.settings.compiler.version)

    @property
    def os(self):
        return {
            "AIX": "aix",
            "Android": "android",
            "FreeBSD": "freebsd",
            "iOS": "iphone",
            "Linux": "linux",
            "Macos": "darwin",
            "SunOS": "solaris",
            "tvOS": "appletv",
            "watchOS": "iphone",
            "Windows": "windows",
            "WindowsStore": "windows",
            "WindowsCE": "windows",
        }.get(str(self.conanfile.settings.os))

    @property
    def address_model(self):
        if self.conanfile.settings.arch in ("x86_64", "ppc64", "ppc64le", "mips64", "armv8", "armv8.3", "sparcv9"):
            return "64"
        else:
            return "32"

    @property
    def architecture(self):
        arch = {
            "arm": "arm",
            "mips": "mips1",
            "mips64": "mips64",
            "ppc": "power",
            "s390": "s390x",
            "sparc": "sparc",
            "x86": "x86",
        }
        for i in arch.items():
            if str(self.conanfile.settings.arch).startswith(i[0]):
                return i[1]
        return None

    @property
    def variant(self):
        return {
            'Debug': 'debug',
            'MinSizeRel': 'minsizerel',
            'Release': 'release',
            'RelWithDebInfo': 'relwithdebinfo',
        }.get(str(self.conanfile.settings.get_safe('build_type')), "debug")

    @property
    def cxxstd(self):
        if self.conanfile.settings.compiler.get_safe('cppstd'):
            return str(self.conanfile.settings.compiler.get_safe('cppstd')).removeprefix("gnu")
        else:
            None

    @property
    def cxxstd_dialect(self):
        return 'gnu' if str(self.conanfile.settings.compiler.get_safe('cppstd')).startswith('gnu') else None

    @property
    def stdlib(self):
        return {
            "libstdc++": "gnu",
            "libstdc++11": "gnu11",
            "libc++": "libc++",
            "libstlport": "sun-stlport",
        }.get(str(self.conanfile.settings.compiler.get_safe("libcxx")), "native")

    @property
    def link(self):
        return "shared" if self.conanfile.options.get_safe(
            "shared", self.conanfile.default_options["shared"]) else "static"

    def _add_flags_os(self):
        self.flags.append("target-os=%s" % (self.os))

    def _add_flags_address_model(self):
        self.flags.append("address-model=%s" % (self.address_model))

    def _add_flags_architecture(self):
        self.flags.append("architecture=%s" % (self.architecture))

    def _add_flags_toolset(self):
        self.flags.append("toolset=%s" % (self.toolset))

    def _add_flags_variant(self):
        if self.variant == "debug":
            self.flags.append("variant=debug")
        elif self.variant == "release":
            self.flags.append("variant=release")
        elif self.variant == "minsizerel":
            self.flags.extend([
                "optimization=space",
                "debug-symbols=off",
                "inlining=full",
                "runtime-debugging=off",
            ])
        elif self.variant == "relwithdebinfo":
            self.flags.extend([
                "optimization=speed",
                "debug-symbols=off",
                "inlining=full",
                "runtime-debugging=off",
            ])

    def _add_flags_cxxstd(self):
        if self.cxxstd:
            self.flags.append("cxxstd=%s" % (self.cxxstd))

    def _add_flags_cxxstd_dialect(self):
        if self.cxxstd_dialect:
            self.flags.append("cxxstd-dialect=%s" % (self.cxxstd_dialect))

    def _add_flags_runtime_link(self):
        if self.toolset == "msvc":
            self.flags.append("runtime-link=%s" % ("static" if "MT" in str(
                self.conanfile.settings.compiler.runtime) else "shared"))

    def _add_flags_runtime_debugging(self):
        if self.toolset == "msvc":
            self.flags.append("runtime-debugging=%" % ("on" if "d" in str(
                self.conanfile.settings.compiler.runtime) else "off"))

    def _add_flags_stdlib(self):
        self.flags.append("stdlib=%s" % (self.stdlib))

    def _add_flags_link(self):
        self.flags.append("link=%s" % (self.link))

    def _add_flags_other(self):
        cxxflags = []
        linkflags = []
        if tools.apple.is_apple_os(self.conanfile):
            if self.conanfile.settings.get_safe("os.version"):
                cxxflags.append(tools.apple.apple_min_version_flag(
                    self.conanfile))
                if self.conanfile.settings.get_safe("os.subsystem") == "catalyst":
                    cxxflags.append("--target=arm64-apple-ios-macabi")
                    link_flags.append("--target=arm64-apple-ios-macabi")
        if self.conanfile.options.get_safe("fPIC", self.conanfile.default_options["fPIC"]):
            cxxflags.append("-fPIC")
        self.flags.extend(["cxxflags=%s" % (f) for f in cxxflags])
        self.flags.extend(["linkflags=%s" % (f) for f in linkflags])
