# **********************************************************************
#
# Copyright (c) 2003-2018 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************

$(test)_client_sources = Test.ice TestI.cpp Client.cpp AllTests.cpp
$(test)_dependencies = TestCommon IceSSL Ice

tests += $(test)
