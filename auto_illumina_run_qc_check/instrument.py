import re

from auto_illumina_run_qc_check.model import InstrumentType

MISEQ_RUN_ID_REGEX = "\\d{6}_M\\d{5}_\\d+_\\d{9}-[A-Z0-9]{5}"
NEXTSEQ_RUN_ID_REGEX = "\\d{6}_VH\\d{5}_\\d+_[A-Z0-9]{9}"
I100_RUN_ID_REGEX = "\\d{8}_SH\\d{5}_\\d+_[A-Z0-9]{10}-[A-Z0-9]{3}"

run_id_regex_by_instrument_type = {
    'miseq': MISEQ_RUN_ID_REGEX,
    'nextseq': NEXTSEQ_RUN_ID_REGEX,
    'i100': I100_RUN_ID_REGEX,
}

def determine_instrument_type(run_id: str) -> InstrumentType:
    """
    Determine the instrument type

    :param run_id: The sequencing run ID.
    :return: The instrument type
    """
    instrument_type_str = "unknown"

    for instrument_type, regex in run_id_regex_by_instrument_type.items():
        if re.match(regex, run_id):
            instrument_type_str = instrument_type

    instrument_type = InstrumentType(instrument_type_str)

    return instrument_type
