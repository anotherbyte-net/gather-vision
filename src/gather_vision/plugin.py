"""Available to plugins."""
import abc

from gather_vision import model


class Entry(abc.ABC):
    """The entry point class for plugins.

    Compatible plugins must implement this class.
    """

    @abc.abstractmethod
    def update(self, args: model.UpdateArgs) -> model.UpdateResult:  # noqa: U100
        """Update the data sources that match the args.

        Args:
            args: The arguments for update.

        Returns:
            The result of the update action.
        """
        raise NotImplementedError("Must implement 'update'.")

    @abc.abstractmethod
    def list(self, args: model.ListArgs) -> model.ListResult:  # noqa: U100
        """List the plugins and data sources that match the args.

        Args:
            args: The arguments for list.

        Returns:
            The result of the list action.
        """
        raise NotImplementedError("Must implement 'list'.")
