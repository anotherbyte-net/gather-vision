"""Available to plugins."""
import abc

from gather_vision import model


class Entry(abc.ABC):
    """The entry point class for plugins.
    Compatible plugins must implement this class."""

    @abc.abstractmethod
    def update(self, args: model.UpdateArgs) -> model.UpdateResult:  # noqa: U100
        """Run the update action.

        Args:
            args: The arguments for update.

        Returns:
            The result of the update action.
        """
        raise NotImplementedError("Must implement 'update'.")

    @abc.abstractmethod
    def show(self, args: model.ShowArgs) -> model.ShowResult:  # noqa: U100
        """Run the show action.

        Args:
            args: The arguments for show.

        Returns:
            The result of the show action.
        """
        raise NotImplementedError("Must implement 'show'.")
