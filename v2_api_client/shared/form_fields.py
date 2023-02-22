from django.core.exceptions import ValidationError
from django.forms import NullBooleanField


class RequiredYesNoRadioButton(NullBooleanField):
    """A required Yes/No radio button field."""

    def validate(self, value):
        if value is None:
            raise ValidationError(self.error_messages['required'], code='required')
        return super().validate(value)
