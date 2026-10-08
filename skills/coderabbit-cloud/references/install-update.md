# Install or update local CodeRabbit skills

`coderabbit skills` reconciles every released CodeRabbit skill for the coding
agents detected on the local machine. The same command installs missing skills
and updates existing CLI-managed or supported externally managed copies.

This is separate from `coderabbit code skills import`, which uploads one local
skill to the cloud library.

## Marketplace plugin boundary

An active official CodeRabbit marketplace plugin owns its bundled skills.
Never install into or update its plugin cache with `coderabbit skills`; the
marketplace updates that plugin.

If the preview identifies an agent as using the `official CodeRabbit plugin`,
do not approve a separate install for that same agent, even when the new skill
is absent from the installed plugin version. Tell the user to update the plugin
through its marketplace. Do not create a second copy beside the plugin.

## Agent flow

1. Make sure `coderabbit skills --help` lists `--agent` and `--confirm`. If it
   does not, report that the installed CLI does not support agent-approved skill
   setup and stop.
2. Run the read-only preview:

   ```sh
   coderabbit skills --agent
   ```

3. Show the complete plan and every destination path to the user. Call out:
   - new installs;
   - updates and externally managed refreshes;
   - locally modified copies that would be replaced;
   - conflicts or project copies left unchanged;
   - marketplace plugin targets, which cannot receive a separate install.
4. If the preview proposes a separate install for an agent with an active
   official CodeRabbit marketplace plugin, stop without asking for approval.
   The user must update that plugin through its marketplace.
5. Otherwise, ask for explicit approval of the exact plan. The last JSON record
   has `action: "confirm_skills_setup"`, a `planHash`, and the exact `command`.
6. After approval, run that exact returned command once, for example:

   ```sh
   coderabbit skills --confirm <plan-hash>
   ```

7. Report installed, updated, failed, and unchanged targets separately.

## Result handling

- A preview changes no skill files.
- A changed plan hash means the detected release, paths, or ownership changed.
  Run a new preview, show it to the user, and get fresh approval.
- If every released skill is already available, report that result and stop.
- If the CLI reports conflicting or duplicate installations, leave them
  unchanged. The user updates or removes them with their owning installer.
- A partial result can update some targets while leaving conflicts unchanged.
  Report both; do not retry failed writes automatically.
- Do not run the interactive `coderabbit skills` form from an agent session.
  Use the preview and exact-confirm flow above.
