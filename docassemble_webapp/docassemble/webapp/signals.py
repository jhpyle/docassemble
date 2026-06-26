from blinker import Namespace
signals = Namespace()

feature_hook = signals.signal('feature_hook')
