# Settings schema and hosted support

## Check the hosted environment

Before generating or recommending a new V3 repository configuration for hosted
reviews, establish that the repository uses GitHub Cloud on CodeRabbit Cloud.
Use known session context or ask for the hosting environment when it is missing.
Each such repository can opt in with numeric `version: 3`. Central configuration
files, other Git hosting platforms, and self-hosted CodeRabbit continue to use
V2. The web app has separate enrollment for its V3 editor. Follow the current
[migration guide](https://docs.coderabbit.ai/guides/migrate-configuration-v3).

Local CLI capability and schema validation establish file compatibility.
Hosted support also depends on the environment above. If the environment is
unknown or requires V2, explain that constraint before generating V3. Continue
an existing V2 configuration through the CLI, or use a documented V2 creation
workflow if the installed CLI provides one. If it only creates V3, report that
capability gap. Read-only validation of an explicitly selected file can proceed
without establishing hosted support.

## Select the settings schema

Agent protocol 2 is the JSON response format for both V2 and V3 settings.
For YAML with numeric top-level `version: 3`, expect the CLI's `schema`
field to be `https://www.coderabbit.ai/integrations/schema.v3.json`.
Existing YAML with no version or numeric `version: 2` uses the V2 schema.
Preserve its version declaration and layout during ordinary edits.
The YAML editor comment alone does not select the settings version.

CLI 0.9.6 generates a new V3 proposal when the repository and signed-in
organization are eligible. Unknown eligibility or an unavailable V3 schema
can produce a V2 proposal. Check the generated proposal's declared version and
returned schema. If a new proposal uses V2, explain the fallback and let the
user choose that V2 proposal or resolve V3 eligibility/schema availability
before regenerating. Use any settled preference from the session. A V2 result
for a new file alone does not establish that the CLI lacks V3 support.
See [agent-guided setup](https://docs.coderabbit.ai/cli#agent-guided-setup).

If the CLI reports the V2 schema for an existing V3 document, stop before
proposing a change or interpreting V2 validation errors as defects in V3 YAML.
A documented V2 creation workflow for an environment requiring V2 can continue.


## Directory-document availability

Instruction and check documents work on GitHub Cloud with CodeRabbit Cloud,
with either V2 or V3 settings. GitHub Enterprise Server, other Git providers,
and self-hosted CodeRabbit do not read them. Establish the hosting environment
before recommending these documents. For unsupported hosting, explain the
limitation and use a supported configuration route.
See [document availability](https://docs.coderabbit.ai/configuration/documents#availability).
