import re

MISEQ_RUN_ID_REGEX = "\\d{6}_M\\d{5}_\\d+_\\d{9}-[A-Z0-9]{5}"
NEXTSEQ_RUN_ID_REGEX = "\\d{6}_VH\\d{5}_\\d+_[A-Z0-9]{9}"
I100_RUN_ID_REGEX = "\\d{8}_SH\\d{5}_\\d+_[A-Z0-9]{10}-[A-Z0-9]{3}"

def determine_instrument_type(run_id: str):
    """
    """
    instrument_type = 'unknown'

    matches_miseq_regex = re.match(MISEQ_RUN_ID_REGEX, run_id)
    matches_nextseq_regex = re.match(NEXTSEQ_RUN_ID_REGEX, run_id)
    matches_i100_regex = re.match(I100_RUN_ID_REGEX, run_id)
    
    if matches_miseq_regex:
        instrument_type = 'miseq'
    elif matches_nextseq_regex:
        instrument_type = 'nextseq'
    elif matches_i100_regex:
        instrument_type = 'i100'

    return instrument_type
