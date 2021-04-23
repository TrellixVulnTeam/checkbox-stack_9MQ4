#!/usr/bin/env python3
from plainbox.provider_manager import setup, N_

# You can inject other stuff here but please don't go overboard.
#
# In particular, if you need comprehensive compilation support to get
# your bin/ populated then please try to discuss that with us in the
# upstream project IRC channel #checkbox on irc.freenode.net.

# NOTE: one thing that you could do here, that makes a lot of sense,
# is to compute version somehow. This may vary depending on the
# context of your provider. Future version of PlainBox will offer git,
# bzr and mercurial integration using the versiontools library
# (optional)

setup(
    name='checkbox-provider-phoronix',
    namespace='com.canonical.certification',
    version="0.8.0rc1",
    description=N_("Checkbox provider with Phoronix Test Suite"),
    gettext_domain="checkbox-provider-phoronix",
)
