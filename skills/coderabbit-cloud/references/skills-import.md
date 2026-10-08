# Import a local skill into the cloud skill library

`coderabbit code skills import` uploads a local skill directory to the cloud
skill library of the selected organization. Cloud tasks can then use it.
Importing does not start a task.

This command has no `--agent` mode. It writes plain text. Without an
interactive terminal, it runs only with an explicit path and `--yes`.

## Procedure

1. Make sure that `coderabbit code skills import --help` lists `--yes` and
   `--scope`. If it does not, report that the installed CLI does not support
   skill import, and stop.
2. Run the import only when the user names the exact skill to upload. If the
   user wants to pick skills from a list, ask them to run
   `coderabbit code skills import` in their own terminal.
3. Confirm the path. It is one skill directory that contains `SKILL.md`, or
   that `SKILL.md` file. A directory that holds several skills is rejected.
4. Omit `--scope` unless the user asks for an access change. Without
   `--scope`, a skill that the user already owns keeps its access, and a new
   skill is private. With `--scope`:
   - `personal`: only the user can use the skill.
   - `organization`: everyone in the selected organization can use it.
5. `--yes` skips the CLI's confirmation prompt. List every file in the skill
   directory for the user first, and get their confirmation.
6. Run one of these commands:

   ```sh
   coderabbit code skills import <skill-path> --yes
   coderabbit code skills import <skill-path> --scope <personal|organization> --yes
   ```

7. Read the exit code:
   - 0: report the output. Each line names a skill, its result (`Imported`,
     `Updated`, `Already up to date`, or `Access updated`), and its access.
     stderr also has one beta notice line with the feedback link. It is not a
     skill result.
   - Not 0: report the error text. Do not rerun it yourself.

## Rules that the cloud library applies

- `SKILL.md` needs YAML `name` and `description` and a body that is not
  empty.
- Hooks, forked contexts, and reserved runtime names are not supported.
- A bundle can be at most 2 MiB, each file at most 1 MiB, and at most 256
  entries, including directories.
- Links inside a skill are rejected.
- The import does not run skill scripts.
- New content creates a new version. The same content is not uploaded
  again. The command never overwrites a skill that another user shared.
- If the access change fails after the save, the error names the saved skill
  ID. The same import, run again when the user asks, finishes the access
  change and creates no new version.
- The server can reject the organization for the skill library. Report its
  message.
