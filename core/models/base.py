from django.db import models

from core.utils.exceptions import ValidationError


class BaseModel(models.Model):
    """
    Base model with common utilities.
    """

    fields_to_ignore = []

    class Meta:
        abstract = True

    @classmethod
    def get_instance(cls, exception_to_raise=ValidationError, **filters):
        """
        Get the class instance and raise an exception if it does not exist.
        """
        try:
            return cls.objects.get(**filters)
        except (cls.DoesNotExist, cls.MultipleObjectsReturned) as e:
            raise exception_to_raise(
                "Instance does not exist or multiple instances found", status=400
            ) from e

    def before_save(self, *args, **kwargs):
        """
        Method triggered before save.
        """
        pass

    def after_save(self, *args, **kwargs):
        """
        Method triggered after save.
        """
        pass

    def save(self, *args, **kwargs):
        """
        Save method that triggers events before and after save.
        """
        self.before_save(*args, **kwargs)
        super().save(*args, **kwargs)
        self.after_save(*args, **kwargs)
        return self

    def set_values(self, values):
        """
        Assign values from a dictionary to the object.
        """
        if not values or not isinstance(values, dict):
            return self

        to_update = {f: v for f, v in values.items() if f not in self.fields_to_ignore}
        for field, value in to_update.items():
            setattr(
                self,
                field,
                value.strip() if isinstance(value, str) else value,
            )
        return self
