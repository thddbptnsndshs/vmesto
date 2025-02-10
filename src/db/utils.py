from typing import Optional

import numpy as np
from pydantic import BaseModel, Field
from ruword_frequency import Frequency
from typing import List

freq = Frequency()
freq.load()


def get_frequencies(written: str, intended: str) -> List[float]:
    english = any([char in 'abcdefghijklmnopqrstuvwxyz' for char in written])
    textlen = len(written.split())
    if not english and textlen == 1:  # TODO: implement eng and multiword frequency computation
        written_ipm = freq.ipm(written)
        intended_ipm = freq.ipm(intended)
        wi_ratio = written_ipm / intended_ipm
    if wi_ratio not in [np.inf, -np.inf, np.nan]:
        return written_ipm, intended_ipm, wi_ratio
    else:
        return [None] * 3


class BaseRequest(BaseModel):
    """
    Base model for all requests, providing a common structure if needed.
    """
    request_id: Optional[str] = Field(
        None, description="Optional unique identifier for the request."
    )


class AddUserRequest(BaseRequest):
    """
    Model for the /add_user endpoint.
    """
    username: int = Field(..., description="Name of the channel to add.")


class AddPairRequest(BaseRequest):
    """
    Model for the /add_pair endpoint.
    """
    written: str = Field(..., description="Word as written.")
    intended: str = Field(..., description="Word as intended.")
    written_ipm: float = Field(..., description="Written word frequency in ipm.")
    intended_ipm: float = Field(..., description="Intended word frequency in ipm.")
    wi_score: float = Field(..., description="Written-intended frequency ratio.")
    user_id: int = Field(..., description="User identifier.")
    datetime: str = Field(..., description="Message date and time in ISO format.")


class SelectPairsRequest(BaseRequest):
    """
    Model for the /select_pairs endpoint.
    """
    username: int = Field(..., description="User identifier.")