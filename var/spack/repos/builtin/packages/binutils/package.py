# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import re


class Binutils(AutotoolsPackage, GNUMirrorPackage):
    """GNU binutils, which contain the linker, assembler, objdump and others"""

    homepage = "https://www.gnu.org/software/binutils/"
    gnu_mirror_path = "binutils/binutils-2.28.tar.bz2"

    maintainers = ['alalazo']

    tags = ['build-tools', 'core-packages']

    executables = ['^nm$', '^readelf$']

    version('2.38', sha256='070ec71cf077a6a58e0b959f05a09a35015378c2d8a51e90f3aeabfe30590ef8')
    version('2.37', sha256='67fc1a4030d08ee877a4867d3dcab35828148f87e1fd05da6db585ed5a166bd4')
    version('2.36.1', sha256='5b4bd2e79e30ce8db0abd76dd2c2eae14a94ce212cfc59d3c37d23e24bc6d7a3')
    version('2.35.2', sha256='cfa7644dbecf4591e136eb407c1c1da16578bd2b03f0c2e8acdceba194bb9d61')
    version('2.35.1', sha256='320e7a1d0f46fcd9f413f1046e216cbe23bb2bce6deb6c6a63304425e48b1942')
    version('2.35', sha256='7d24660f87093670738e58bcc7b7b06f121c0fcb0ca8fc44368d675a5ef9cff7')
    version('2.34', sha256='89f010078b6cf69c23c27897d686055ab89b198dddf819efb0a4f2c38a0b36e6')
    version('2.33.1', sha256='0cb4843da15a65a953907c96bad658283f3c4419d6bcc56bf2789db16306adb2')
    version('2.32',   sha256='de38b15c902eb2725eac6af21183a5f34ea4634cb0bcef19612b50e5ed31072d')
    version('2.31.1', sha256='ffcc382695bf947da6135e7436b8ed52d991cf270db897190f19d6f9838564d0')
    version('2.29.1', sha256='1509dff41369fb70aed23682351b663b56db894034773e6dbf7d5d6071fc55cc')
    version('2.28', sha256='6297433ee120b11b4b0a1c8f3512d7d73501753142ab9e2daa13c5a3edd32a72')
    version('2.27', sha256='369737ce51587f92466041a97ab7d2358c6d9e1b6490b3940eb09fb0a9a6ac88')
    version('2.26', sha256='c2ace41809542f5237afc7e3b8f32bb92bc7bc53c6232a84463c423b0714ecd9')
    version('2.25.1', sha256='b5b14added7d78a8d1ca70b5cb75fef57ce2197264f4f5835326b0df22ac9f22')
    version('2.25', sha256='22defc65cfa3ef2a3395faaea75d6331c6e62ea5dfacfed3e2ec17b08c882923')
    version('2.24', sha256='e5e8c5be9664e7f7f96e0d09919110ab5ad597794f5b1809871177a0f0f14137')
    version('2.23.2', sha256='fe914e56fed7a9ec2eb45274b1f2e14b0d8b4f41906a5194eac6883cfe5c1097')
    version('2.20.1', sha256='71d37c96451333c5c0b84b170169fdcb138bbb27397dc06281905d9717c8ed64')

    variant('plugins', default=True,
            description="enable plugins, needed for gold linker")
    variant('gold', default=False,
            description="build the gold linker")
    variant('libiberty', default=False, description='Also install libiberty.')
    variant('nls', default=True, description='Enable Native Language Support')
    variant('headers', default=False, description='Install extra headers (e.g. ELF)')
    variant('lto', default=False, description='Enable lto.')
    variant('ld', default=False, description='Enable ld.')
    variant('gas', default=False, description='Enable as assembler.')
    variant('interwork', default=False, description='Enable interwork.')
    variant('libs', default='shared,static', values=('shared', 'static'),
            multi=True, description='Build shared libs, static libs or both')

    patch('cr16.patch', when='@:2.29.1')
    patch('update_symbol-2.26.patch', when='@2.26')

    # 2.36 is missing some dependencies, this patch allows a parallel build.
    # https://sourceware.org/bugzilla/show_bug.cgi?id=27482
    patch('parallel-build-2.36.patch', when='@2.36')

    depends_on('zlib')
    depends_on('diffutils', type='build')
    depends_on('gettext', when='+nls')

    # Prior to 2.30, gold did not distribute the generated files and
    # thus needs bison, even for a one-time build.
    depends_on('m4', type='build', when='@:2.29 +gold')
    depends_on('bison', type='build', when='@:2.29 +gold')

    # 2.38 with +gas needs makeinfo due to a bug, see:
    # https://sourceware.org/bugzilla/show_bug.cgi?id=28909
    depends_on('texinfo', type='build', when='@2.38 +gas')
    # 2.34 needs makeinfo due to a bug, see:
    # https://sourceware.org/bugzilla/show_bug.cgi?id=25491
    depends_on('texinfo', type='build', when='@2.34')

    conflicts('+gold', when='platform=darwin',
              msg="Binutils cannot build linkers on macOS")

    # When you build binutils with ~ld and +gas and load it in your PATH, you
    # may end up with incompatibilities between a potentially older system ld
    # and a recent assembler. For instance the linker on ubuntu 16.04 from
    # binutils 2.26 and the assembler from binutils 2.36.1 will result in:
    # "unable to initialize decompress status for section .debug_info"
    # when compiling with debug symbols on gcc.
    conflicts('+gas', '~ld', msg="Assembler not always compatible with system ld")

    # When you build ld.gold you automatically get ld, even when you add the
    # --disable-ld flag
    conflicts('~ld', '+gold')

    @classmethod
    def determine_version(cls, exe):
        output = Executable(exe)('--version', output=str, error=str)
        match = re.search(r'GNU (nm|readelf).* (\S+)', output)
        return Version(match.group(2)).dotted.up_to(3) if match else None

    def setup_build_environment(self, env):

        if self.spec.satisfies('%cce'):
            env.append_flags('LDFLAGS', '-Wl,-z,muldefs')

        if '+nls' in self.spec:
            env.append_flags('LDFLAGS', '-lintl')

    def configure_args(self):
        spec = self.spec

        args = [
            '--disable-dependency-tracking',
            '--disable-werror',
            '--enable-multilib',
            '--enable-64-bit-bfd',
            '--enable-targets=all',
            '--with-system-zlib',
            '--with-sysroot=/',
        ]

        args += self.enable_or_disable('libs')
        args += self.enable_or_disable('lto')
        args += self.enable_or_disable('ld')
        args += self.enable_or_disable('gas')
        args += self.enable_or_disable('interwork')
        args += self.enable_or_disable('gold')
        args += self.enable_or_disable('plugins')

        if '+libiberty' in spec:
            args.append('--enable-install-libiberty')
        else:
            args.append('--disable-install-libiberty')

        if '+nls' in spec:
            args.append('--enable-nls')
        else:
            args.append('--disable-nls')

        # To avoid namespace collisions with Darwin/BSD system tools,
        # prefix executables with "g", e.g., gar, gnm; see Homebrew
        # https://github.com/Homebrew/homebrew-core/blob/master/Formula/binutils.rb
        if spec.satisfies('platform=darwin'):
            args.append('--program-prefix=g')

        return args

    @run_after('install')
    def install_headers(self):
        # some packages (like TAU) need the ELF headers, so install them
        # as a subdirectory in include/extras
        if '+headers' in self.spec:
            extradir = join_path(self.prefix.include, 'extra')
            mkdirp(extradir)
            # grab the full binutils set of headers
            install_tree('include', extradir)
            # also grab the headers from the bfd directory
            install(join_path(self.build_directory, 'bfd', '*.h'),
                    extradir)

    def flag_handler(self, name, flags):
        # Use a separate variable for injecting flags. This way, installing
        # `binutils cflags='-O2'` will still work as expected.
        iflags = []
        # To ignore the errors of narrowing conversions for
        # the Fujitsu compiler
        if name == 'cxxflags' and (
            self.spec.satisfies('@:2.31.1') and
            self.compiler.name in ('fj', 'clang', 'apple-clang')
        ):
            iflags.append('-Wno-narrowing')
        elif name == 'cflags':
            if self.spec.satisfies('@:2.34 %gcc@10:'):
                iflags.append('-fcommon')
            if self.spec.satisfies('%cce'):
                iflags.append('-fPIC -fcommon')
        elif name == 'ldflags':
            if self.spec.satisfies('%cce'):
                iflags.append('-Wl,-z,notext')
        return (iflags, None, flags)

    def test(self):
        spec_vers = str(self.spec.version)

        checks = {
            'ar': spec_vers,
            'c++filt': spec_vers,
            'coffdump': spec_vers,
            'dlltool': spec_vers,
            'elfedit': spec_vers,
            'gprof': spec_vers,
            'ld': spec_vers,
            'nm': spec_vers,
            'objdump': spec_vers,
            'ranlib': spec_vers,
            'readelf': spec_vers,
            'size': spec_vers,
            'strings': spec_vers,
        }

        for exe in checks:
            expected = checks[exe]
            reason = 'test: ensuring version of {0} is {1}' \
                .format(exe, expected)
            self.run_test(exe, '--version', expected, installed=True,
                          purpose=reason, skip_missing=True)
