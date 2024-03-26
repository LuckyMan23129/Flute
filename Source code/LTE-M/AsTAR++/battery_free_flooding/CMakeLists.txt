# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(battery_free_flooding)

include_directories("include/")
set(SOURCES src/modem.c include/modem.h include/battery.h src/battery.c)

target_sources(app PRIVATE src/main.c src/modem.c src/battery.c)

#zephyr_include_directories(src)