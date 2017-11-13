from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools, CMake
from conans.tools import download, unzip, replace_in_file, run_in_windows_bash, build_sln_command, os_info, SystemPackageTool
from conans.util.files import load
import os, re

def replace_in_file_regex(file_path, search, replace):
    content = load(file_path)
    content = re.sub(search, replace, content)
    content = content.encode("utf-8")
    with open(file_path, "wb") as handle:
        handle.write(content)

class OggConan(ConanFile):
    name = "ogg"
    version = "master"
    sources_folder = "sources"
    generators = "cmake"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    url="https://github.com/bincrafters/conan-ogg"
    description="The OGG library"
    requires = ""
    license="BSD"
    exports = "FindOGG.cmake"
    exports_sources = ["CMakeLists.txt"]

    def configure(self):
        del self.settings.compiler.libcxx

        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def source(self):
        if self.version == "master":
            zip_name = "%s.zip" % self.version
        else:
            zip_name ="v%s.zip" % self.version

        download("https://github.com/xiph/ogg/archive/%s" % zip_name, zip_name)

        unzip(zip_name)
        os.unlink(zip_name)
        os.rename("%s-%s" % (self.name, self.version), self.sources_folder)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        return

    def package(self):
        self.copy("FindOGG.cmake", ".", ".")
        self.copy(pattern="*.h", dst="include/ogg", keep_path=False)
        self.copy("%s/copying*" % self.sources_folder, dst="licenses",  ignore_case=True, keep_path=False)

        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.pdb", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
        else:
            if self.options.shared:
                if self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", keep_path=False)
                elif self.settings.os == "Windows":
                    self.copy(pattern="*.dll", dst="bin", keep_path=False)
                    self.copy(pattern="*.dll.a", dst="lib", keep_path=False)
                else:
                    self.copy(pattern="*.so*", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*g.a", dst="lib", keep_path=False)
     
    def package_info(self):
        if self.settings.compiler == "Visual Studio" and self.version == "1.3.2":
            if self.options.shared:
                self.cpp_info.libs = ['libogg']
            else:
                self.cpp_info.libs = ['libogg_static']             
        else:
            self.cpp_info.libs = ['ogg']
