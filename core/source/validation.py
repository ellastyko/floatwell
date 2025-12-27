class SourceValidationError(ValueError):
    pass

class SourceValidator:
     # -------------------- entrypoint --------------------

    @staticmethod
    def validate_source(source: dict):
        if not isinstance(source, dict):
            raise SourceValidationError("Source must be a dict")

        SourceValidator.require_key(source, 'globals')
        SourceValidator.require_key(source, 'assets')

        SourceValidator.validate_globals(source['globals'])
        SourceValidator.validate_assets(source['assets'])

    
    # -------------------- globals --------------------

    @staticmethod
    def validate_globals(settings: dict, path="globals"):
        SourceValidator.require_dict(settings, path)

        filters = settings.get('strategies')
        if filters is not None:
            SourceValidator.require_dict(filters, f"{path}.strategies")

            modes = filters.get('mode')
            if modes is not None:
                SourceValidator.require_list(modes, f"{path}.filters.mode")

                allowed = {'pattern', 'float', 'keychain', 'sticker'}
                for i, mode in enumerate(modes):
                    SourceValidator.require_str(mode, f"{path}.filters.mode[{i}]")
                    if mode not in allowed:
                        raise SourceValidationError(
                            f"{path}.filters.mode[{i}] invalid value '{mode}'"
                        )

        # -------- exteriors --------
        exteriors = settings.get('exteriors')
        if exteriors is not None:
            SourceValidator.require_dict(exteriors, f"{path}.exteriors")

            for alias, full in exteriors.items():
                SourceValidator.require_str(
                    alias,
                    f"{path}.exteriors.<alias>"
                )
                SourceValidator.require_str(
                    full,
                    f"{path}.exteriors.{alias}"
                )

    # -------------------- assets --------------------

    @staticmethod
    def validate_assets(configs: dict, path="assets"):
        SourceValidator.require_dict(configs, path)

        for cname, config in configs.items():
            SourceValidator.require_str(cname, f"{path}.<item_name>")
            SourceValidator.require_dict(config, f"{path}.{cname}")

            SourceValidator.optional_bool(config, 'enabled', path, cname)
            SourceValidator.optional_bool(config, 'has_exteriors', path, cname)
            SourceValidator.optional_bool(config, 'multipage', path, cname)
            SourceValidator.optional_dict(config, 'strategies', path, cname)

            if 'exteriors' in config:
                SourceValidator.require_list(
                    config['exteriors'],
                    f"{path}.{cname}.exteriors"
                )

            strategies = config.get('strategies')

            # При наличии strategies мы и
            if strategies:
                # -------- pattern --------
                if 'pattern' in strategies:
                    SourceValidator._validate_pattern_strategy(cname, path, strategies)
                    
    @staticmethod
    def _validate_pattern_strategy(cname, path, strategies):
        SourceValidator.require_dict(
            strategies['pattern'],
            f"{path}.{cname}.strategies.pattern"
        )

        for pname, pdata in strategies['pattern'].items():
            SourceValidator.require_dict(
                pdata,
                f"{path}.{cname}.strategies.pattern.{pname}"
            )

            if 'values' in pdata:
                SourceValidator.require_list(
                    pdata['values'],
                    f"{path}.{cname}.strategies.pattern.{pname}.values"
                )

            if 'price_tolerance' in pdata:
                pt = pdata['price_tolerance']
                pt_path = f"{path}.{cname}.strategies.pattern.{pname}.price_tolerance"

                # Вариант 1: число
                if isinstance(pt, (int, float)):
                    pass  # ок

                # Вариант 2: dict по exterior
                elif isinstance(pt, dict):
                    for ext, val in pt.items():
                        SourceValidator.require_number(
                            val,
                            f"{pt_path}.{ext}"
                        )

                else:
                    raise SourceValidationError(
                        f"{pt_path} must be a number or dict"
                    )
    
    # -------------------- helpers --------------------

    @staticmethod
    def require_key(obj, key):
        if key not in obj:
            raise SourceValidationError(f"Missing '{key}'")

    @staticmethod
    def require_dict(value, path):
        if not isinstance(value, dict):
            raise SourceValidationError(f"{path} must be a dict")

    @staticmethod
    def require_list(value, path):
        if not isinstance(value, list):
            raise SourceValidationError(f"{path} must be a list")

    @staticmethod
    def require_bool(value, path):
        if not isinstance(value, bool):
            raise SourceValidationError(f"{path} must be a boolean")

    @staticmethod
    def require_str(value, path):
        if not isinstance(value, str):
            raise SourceValidationError(f"{path} must be a string")

    @staticmethod
    def require_number(value, path):
        if not isinstance(value, (int, float)):
            raise SourceValidationError(f"{path} must be a number")

    @staticmethod
    def optional_bool(config, key, path, cname):
        if key in config:
            SourceValidator.require_bool(
                config[key],
                f"{path}.{cname}.{key}"
            )

    @staticmethod
    def optional_dict(config, key, path, cname):
        if key in config:
            SourceValidator.require_dict(
                config[key],
                f"{path}.{cname}.{key}"
            )




