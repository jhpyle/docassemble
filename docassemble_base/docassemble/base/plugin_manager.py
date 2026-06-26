import pluggy
from . import hookspecs


class DocassemblePluginManager(pluggy.PluginManager):
    """PluginManager that merges hookimpl kwargnames into argnames on registration.

    pluggy only dispatches params listed in HookImpl.argnames (params without
    defaults). Params with defaults land in kwargnames and are never filled from
    caller_kwargs. By merging kwargnames into argnames after each register() call,
    and having wrapper callers always supply every param, hookimpls can keep their
    natural Python default-argument signatures.
    """

    def register(self, plugin, name=None):
        result = super().register(plugin, name=name)
        self._merge_kwargnames(plugin)
        return result

    def _merge_kwargnames(self, plugin):
        for attr in dir(self.hook):
            hook_caller = getattr(self.hook, attr, None)
            if hook_caller is None or not hasattr(hook_caller, 'get_hookimpls'):
                continue
            for impl in hook_caller.get_hookimpls():
                if impl.plugin is plugin and impl.kwargnames:
                    impl.argnames = impl.argnames + impl.kwargnames
                    impl.kwargnames = ()


pm = DocassemblePluginManager("docassemble")
pm.add_hookspecs(hookspecs)
