"""Functions to save and load beam projects."""


class ProjectManager:
    """Handles serialization of beam configurations."""

    def save(self, model, path):
        """Save the model to disk.

        Parameters
        ----------
        model : dict
            Data structure describing the project.
        path : str or PathLike
            Destination file where the model will be stored.
        """
        import json

        with open(path, "w", encoding="utf-8") as fh:
            json.dump(model, fh)

    def load(self, path):
        """Load the model from disk.

        Parameters
        ----------
        path : str or PathLike
            Source file previously created with :meth:`save`.

        Returns
        -------
        dict
            Reconstructed project model.
        """
        import json

        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)

