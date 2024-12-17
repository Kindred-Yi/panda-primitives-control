# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.10

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /workspace/libfranka

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /workspace/libfranka/build

# Include any dependencies generated for this target.
include examples/CMakeFiles/motion_with_control.dir/depend.make

# Include the progress variables for this target.
include examples/CMakeFiles/motion_with_control.dir/progress.make

# Include the compile flags for this target's objects.
include examples/CMakeFiles/motion_with_control.dir/flags.make

examples/CMakeFiles/motion_with_control.dir/motion_with_control.cpp.o: examples/CMakeFiles/motion_with_control.dir/flags.make
examples/CMakeFiles/motion_with_control.dir/motion_with_control.cpp.o: ../examples/motion_with_control.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/workspace/libfranka/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object examples/CMakeFiles/motion_with_control.dir/motion_with_control.cpp.o"
	cd /workspace/libfranka/build/examples && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/motion_with_control.dir/motion_with_control.cpp.o -c /workspace/libfranka/examples/motion_with_control.cpp

examples/CMakeFiles/motion_with_control.dir/motion_with_control.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/motion_with_control.dir/motion_with_control.cpp.i"
	cd /workspace/libfranka/build/examples && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /workspace/libfranka/examples/motion_with_control.cpp > CMakeFiles/motion_with_control.dir/motion_with_control.cpp.i

examples/CMakeFiles/motion_with_control.dir/motion_with_control.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/motion_with_control.dir/motion_with_control.cpp.s"
	cd /workspace/libfranka/build/examples && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /workspace/libfranka/examples/motion_with_control.cpp -o CMakeFiles/motion_with_control.dir/motion_with_control.cpp.s

examples/CMakeFiles/motion_with_control.dir/motion_with_control.cpp.o.requires:

.PHONY : examples/CMakeFiles/motion_with_control.dir/motion_with_control.cpp.o.requires

examples/CMakeFiles/motion_with_control.dir/motion_with_control.cpp.o.provides: examples/CMakeFiles/motion_with_control.dir/motion_with_control.cpp.o.requires
	$(MAKE) -f examples/CMakeFiles/motion_with_control.dir/build.make examples/CMakeFiles/motion_with_control.dir/motion_with_control.cpp.o.provides.build
.PHONY : examples/CMakeFiles/motion_with_control.dir/motion_with_control.cpp.o.provides

examples/CMakeFiles/motion_with_control.dir/motion_with_control.cpp.o.provides.build: examples/CMakeFiles/motion_with_control.dir/motion_with_control.cpp.o


# Object files for target motion_with_control
motion_with_control_OBJECTS = \
"CMakeFiles/motion_with_control.dir/motion_with_control.cpp.o"

# External object files for target motion_with_control
motion_with_control_EXTERNAL_OBJECTS =

examples/motion_with_control: examples/CMakeFiles/motion_with_control.dir/motion_with_control.cpp.o
examples/motion_with_control: examples/CMakeFiles/motion_with_control.dir/build.make
examples/motion_with_control: examples/libexamples_common.a
examples/motion_with_control: /usr/lib/libPocoFoundation.so.50
examples/motion_with_control: libfranka.so.0.7.1
examples/motion_with_control: /usr/lib/x86_64-linux-gnu/libpcre.so
examples/motion_with_control: /usr/lib/x86_64-linux-gnu/libz.so
examples/motion_with_control: examples/CMakeFiles/motion_with_control.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/workspace/libfranka/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking CXX executable motion_with_control"
	cd /workspace/libfranka/build/examples && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/motion_with_control.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
examples/CMakeFiles/motion_with_control.dir/build: examples/motion_with_control

.PHONY : examples/CMakeFiles/motion_with_control.dir/build

examples/CMakeFiles/motion_with_control.dir/requires: examples/CMakeFiles/motion_with_control.dir/motion_with_control.cpp.o.requires

.PHONY : examples/CMakeFiles/motion_with_control.dir/requires

examples/CMakeFiles/motion_with_control.dir/clean:
	cd /workspace/libfranka/build/examples && $(CMAKE_COMMAND) -P CMakeFiles/motion_with_control.dir/cmake_clean.cmake
.PHONY : examples/CMakeFiles/motion_with_control.dir/clean

examples/CMakeFiles/motion_with_control.dir/depend:
	cd /workspace/libfranka/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /workspace/libfranka /workspace/libfranka/examples /workspace/libfranka/build /workspace/libfranka/build/examples /workspace/libfranka/build/examples/CMakeFiles/motion_with_control.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : examples/CMakeFiles/motion_with_control.dir/depend

