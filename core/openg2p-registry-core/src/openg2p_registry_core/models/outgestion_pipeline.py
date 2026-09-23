import json

from datetime import datetime
from decimal import Decimal
from uuid import UUID
from enum import Enum
from pathlib import Path
from dataclasses import is_dataclass, asdict

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, validates
from openg2p_fastapi_common.models import BaseORMModel

from .data_models import ProcessStatusEnum


class UniversalJSONEncoder(json.JSONEncoder):
    """
    JSON encoder that handles common Python types not natively
    serializable by json.dumps() — datetime, Decimal, UUID, Enum,
    sets, bytes, Path, dataclasses, and generic objects.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, (set, frozenset)):
            return list(obj)
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode("utf-8", errors="replace")
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, Enum):
            return obj.value
        if is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return super().default(obj)


class OutgoingRawData(BaseORMModel):

    __tablename__ = "outgoing_raw_data"

    outgest_id: Mapped[str] = mapped_column(String, primary_key=True)
    payload_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    change_request_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    intake_form_submission_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    internal_record_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    register_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    data_model_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    topic_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.now())

    changed_by: Mapped[str] = mapped_column(String, nullable=False)
    changed_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    approved_by: Mapped[str] = mapped_column(String, nullable=True)
    approved_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    changed_by_partner_id: Mapped[str] = mapped_column(String, nullable=True, index=True)

    transformation_status: Mapped[str] = mapped_column(String, nullable=False, index=True, default=ProcessStatusEnum.PENDING.value)
    transformation_datetime: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    transformation_latest_error_code: Mapped[str] = mapped_column(String, nullable=True)
    transformation_number_of_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    publish_status: Mapped[str] = mapped_column(String, nullable=True, index=True, default=None)
    publish_datetime: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    publish_latest_error_code: Mapped[str] = mapped_column(String, nullable=True)
    publish_number_of_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

class OutgoingRawDataPayload(BaseORMModel):

    __tablename__ = "outgoing_raw_data_payloads"

    payload_id: Mapped[str] = mapped_column(String, primary_key=True)
    change_request_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    intake_form_submission_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    raw_data_json: Mapped[JSONB] = mapped_column(JSONB, nullable=True)
    raw_data_xml: Mapped[Text] = mapped_column(Text, nullable=True)
    raw_data_text: Mapped[str] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index(
            "ix_outgoing_raw_data_payloads_raw_data_text_gin",
            "raw_data_text",
            postgresql_using="gin",
            postgresql_ops={"raw_data_text": "gin_trgm_ops"},
        ),
    )

    @validates("raw_data_json")
    def update_raw_data_text(self, key, value):
        if value:
            if isinstance(value, (dict, list)):
                # Round-trip through the encoder so both raw_data_text and the
                # JSONB column are free of Decimal/datetime/UUID/etc. SQLAlchemy
                # uses the stdlib json encoder for JSONB, which cannot handle them.
                value = json.loads(json.dumps(value, cls=UniversalJSONEncoder))
                self.raw_data_text = json.dumps(value)
            else:
                self.raw_data_text = str(value)
        return value

class OutgoingTransformedDataPayload(BaseORMModel):

    __tablename__ = "outgoing_transformed_data_payloads"

    outgest_id: Mapped[str] = mapped_column(String, primary_key=True)
    payload_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    change_request_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    intake_form_submission_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    transformed_data_json: Mapped[JSONB] = mapped_column(JSONB, nullable=True)
    transformed_data_xml: Mapped[Text] = mapped_column(Text, nullable=True)
