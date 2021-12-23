class Metadata:
    def version(self):
        from_file = None
        try:
            from_file = self._from_file("tool", "poetry", "version")
        except ValueError:
            pass

        if from_file:
            return from_file

        return self._from_package_version()

    def documentation_url(self):
        from_file = None
        try:
            from_file = self._from_file("tool", "poetry", "documentation")
        except ValueError:
            pass

        if from_file:
            return from_file

        from_package = self._from_package("Project-URL")
        prefix = "Documentation"
        prefix_len = len(prefix)
        for i in from_package:
            if i.startswith(prefix):
                result = i[prefix_len:].strip(" ,")
                return result
        return None

    def _from_file(self, *args):
        from importlib.resources import path

        with path("gather_vision", "apps.py") as p:
            tom_path = (p.parent.parent / "pyproject.toml").absolute()
            if tom_path.exists():
                import toml

                with open(tom_path, "rt") as f:
                    current = toml.load(f)
                    levels = []
                    for arg in args:
                        levels.append(arg)
                        new_item = current.get(arg)
                        if not new_item:
                            raise ValueError(
                                f"Cannot find '{'.'.join(levels)}' in pyproject.toml."
                            )
                        current = new_item
                    return current
        return None

    def _from_package(self, key: str):
        from importlib import metadata

        data = metadata.metadata("gather-vision")

        result = {}
        for index, i in enumerate(data):
            if i not in result:
                result[i] = []
            result[i].append(data.values()[index])

        return result.get(key)

    def _from_package_version(self):
        from importlib import metadata

        ver = metadata.version("gather-vision")
        return ver
