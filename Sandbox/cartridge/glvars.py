# ------
# engine-related code, do not modify!
# --------

registry = set()
libname_to_alias_mapping = dict()

def get_alias(origin_lib_name):
    return libname_to_alias_mapping[origin_lib_name]

def has_registered(origin_lib_name):
    return origin_lib_name in libname_to_alias_mapping

def register_lib(alias, libname, value):  # handy for dependency injection
    global registry, libname_to_alias_mapping
    libname_to_alias_mapping[libname] = alias
    if alias in registry:
        raise KeyError(f'Cannot register lib "{alias}" more than once!')
    globals()[alias] = value
    registry.add(alias)


# ------
# put here, all the custom code added by the gamedev
# --------
font_obj = None
screen_center = None

# represent game constants, by using capitals
MY_CONST = 0
