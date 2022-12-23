from botocore.handlers import _get_presigned_url_source_and_destination_regions, \
    _get_cross_region_presigned_url


async def inject_presigned_url_ec2(params, request_signer, model, **kwargs):
    # The customer can still provide this, so we should pass if they do.
    if 'PresignedUrl' in params['body']:
        return
    src, dest = _get_presigned_url_source_and_destination_regions(
        request_signer, params['body'])
    url = await _get_cross_region_presigned_url(
        request_signer, params, model, src, dest)
    params['body']['PresignedUrl'] = url
    # EC2 Requires that the destination region be sent over the wire in
    # addition to the source region.
    params['body']['DestinationRegion'] = dest


async def inject_presigned_url_rds(params, request_signer, model, **kwargs):
    # SourceRegion is not required for RDS operations, so it's possible that
    # it isn't set. In that case it's probably a local copy so we don't need
    # to do anything else.
    if 'SourceRegion' not in params['body']:
        return

    src, dest = _get_presigned_url_source_and_destination_regions(
        request_signer, params['body'])

    # Since SourceRegion isn't actually modeled for RDS, it needs to be
    # removed from the request params before we send the actual request.
    del params['body']['SourceRegion']

    if 'PreSignedUrl' in params['body']:
        return

    url = await _get_cross_region_presigned_url(
        request_signer, params, model, src, dest)
    params['body']['PreSignedUrl'] = url
