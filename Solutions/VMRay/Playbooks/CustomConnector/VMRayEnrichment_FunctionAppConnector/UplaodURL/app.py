"""
Main Function
"""

# pylint: disable=logging-fstring-interpolation
import logging
import traceback
from json import dumps

import azure.functions as func

from vmray_api import VMRay


def build_submission_data(data):
    """Process a submission response from VMRay Platform

    Args:
        data: (dict): submission response
    """
    jobs_list = []
    jobs = data.get("jobs", [])
    for job in jobs:
        if isinstance(job, dict):
            job_entry = {}
            job_entry["JobID"] = job.get("job_id")
            job_entry["Created"] = job.get("job_created")
            job_entry["SampleID"] = job.get("job_sample_id")
            job_entry["VMName"] = job.get("job_vm_name")
            job_entry["VMID"] = job.get("job_vm_id")
            job_entry["JobRuleSampleType"] = job.get("job_jobrule_sampletype")
            jobs_list.append(job_entry)

    samples_list = []
    samples = data.get("samples", [])
    for sample in samples:
        if isinstance(sample, dict):
            sample_entry = {}
            sample_entry["SampleID"] = sample.get("sample_id")
            sample_entry["SampleURL"] = sample.get("sample_webif_url")
            sample_entry["Created"] = sample.get("sample_created")
            sample_entry["FileName"] = sample.get("submission_filename")
            sample_entry["FileSize"] = sample.get("sample_filesize")
            sample_entry["SSDeep"] = sample.get("sample_ssdeephash")
            sample_entry["SHA1"] = sample.get("sample_sha1hash")
            samples_list.append(sample_entry)

    submissions_list = []
    submissions = data.get("submissions", [])
    for submission in submissions:
        if isinstance(submission, dict):
            submission_entry = {}
            submission_entry["SubmissionID"] = submission.get("submission_id")
            submission_entry["SubmissionURL"] = submission.get("submission_webif_url")
            submission_entry["SampleID"] = submission.get("submission_sample_id")
            submissions_list.append(submission_entry)

    entry_context = {}
    entry_context["vmray_job"] = jobs_list
    entry_context["vmray_sample"] = samples_list
    entry_context["vmray_submission"] = submissions_list

    return entry_context


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    This function handles VMRay API and returns HTTP response
    :param req: func.HttpRequest
    """
    logging.info(f"Resource Requested: {func.HttpRequest}")

    try:
        url = req.params.get("url") or req.get_json().get("url")
        shareable = req.params.get("shareable") or req.get_json().get("shareable")
        max_jobs = req.params.get("max_jobs") or req.get_json().get("max_jobs")
        tags = req.params.get("tags", []) or req.get_json().get("tags", [])
        net_scheme_name = req.params.get("net_scheme_name", []) or req.get_json().get(
            "net_scheme_name"
        )

        if not url:
            return func.HttpResponse(
                "Invalid Request. Missing 'url' parameter.", status_code=400
            )
        vmray = VMRay(logging)
        params = {"shareable": shareable == "true"}
        if max_jobs:
            if (
                isinstance(max_jobs, str)
                and max_jobs.isdigit()
                or isinstance(max_jobs, int)
            ):
                params["max_jobs"] = int(max_jobs)
            else:
                raise ValueError("max_jobs arguments isn't a number")
        if tags:
            params["tags"] = ",".join(tags)
        if net_scheme_name:
            params["user_config"] = (
                '{"net_scheme_name": "' + str(net_scheme_name) + '"}'
            )
        endpoint = "/rest/sample/submit"
        params["sample_url"] = url
        response = vmray.request_vmray_api("POST", endpoint, params)
        submission_data = build_submission_data(response)
        return func.HttpResponse(
            dumps(submission_data),
            headers={"Content-Type": "application/json"},
            status_code=200,
        )
    except KeyError as ke:
        logging.error(f"Invalid Settings. {ke.args} configuration is missing.")
        return func.HttpResponse(
            "Invalid Settings. Configuration is missing.", status_code=500
        )
    except Exception as ex:
        error_detail = traceback.format_exc()
        logging.error(f"Exception Occurred: {str(ex)}, Traceback {error_detail}")
        return func.HttpResponse("Internal Server Exception", status_code=500)
