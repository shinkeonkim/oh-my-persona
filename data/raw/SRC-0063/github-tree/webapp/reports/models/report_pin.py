import hashlib
import secrets

from django.db import models

from common.models import BaseModel


class ReportPin(BaseModel):
    """
    Report Pin model
    """

    class Meta:
        db_table = "report_pins"
        verbose_name = "Report Pin"
        verbose_name_plural = "Report Pins"

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="report_pin",
        verbose_name="User",
    )

    pin_hash = models.CharField(
        max_length=256,
        verbose_name="Pin Hash",
    )

    enabled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Enabled At",
    )

    def get_pin_hash(self, pin: str) -> str:
        user_id = getattr(self, "user_id", None)
        if not user_id:
            raise ValueError("user_id is required to compute pin hash")

        salt = str(user_id)
        return hashlib.sha256((salt + pin).encode()).hexdigest()

    def verify_pin(self, pin: str) -> bool:
        """
        Verify a plain pin against the stored pin_hash using the same salt.
        Returns False if pin_hash isn't set or user_id is not available.
        """

        if not self.pin_hash:
            return False

        try:
            expected = self.get_pin_hash(pin)
        except ValueError:
            return False

        return secrets.compare_digest(self.pin_hash, expected)
