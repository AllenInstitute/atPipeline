from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution('atpipeline').version
except DistributionNotFound:
    __version__ = "0.0.0-not_installed"
