# `backend/.env.tests.e2e.secret`

- [What is `backend/.env.tests.e2e.secret`](#what-is-backendenvtestse2esecret)
- [`LMS_API_BASE_URL`](#lms_api_base_url)
- [`LMS_API_KEY`](#lms_api_key)

## What is `backend/.env.tests.e2e.secret`

`backend/.env.tests.e2e.secret` is a [`.env` file](./environments.md#env-file) that stores [environment variables](./environments.md#environment-variable) for running [end-to-end tests](./quality-assurance.md#end-to-end-test).

Default values: [`backend/.env.tests.e2e.example`](../backend/.env.tests.e2e.example)

> It was added to [`.gitignore`](./git.md#gitignore) because it may contain [secrets](./environments.md#secrets) such as the [LMS API key](./lms-api.md#lms-api-key) or the [VM IP address](./vm.md#your-vm-ip-address).

## `LMS_API_BASE_URL`

See [LMS API base URL](./lms-api.md#lms-api-base-url).

Example: `http://192.0.2.1:42002`

## `LMS_API_KEY`

The [LMS API key](./lms-api.md#lms-api-key).

It value must match the value of [`LMS_API_KEY`](./dotenv-docker-secret.md#lms_api_key) in [`.env.docker.secret`](./dotenv-docker-secret.md#what-is-envdockersecret) used for deployment.
