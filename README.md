# Minecraft Refresh Collection

Community-maintained re-releases of abandoned Minecraft data packs & mods, updated for current versions of Minecraft.

All projects in this collection were originally created by **[lukidonu](https://modrinth.com/user/lukidonu)**, who has [discontinued all of their projects](https://www.curseforge.com/members/lukidon/projects) (*"Projects are discontinued #RIP"*). I tried to contact the author without success, and am maintaining these to keep them alive and compatible with the latest Minecraft.

> **Original author:** [lukidonu](https://modrinth.com/user/lukidonu) &nbsp;•&nbsp; **Maintained by:** [darkstarworks](https://modrinth.com/user/darkstarworks)
>
> **Are you lukidonu?** Please reach out — darkstarworks@gmail.com. Happy to hand a project back or take it down on request.

## Projects

| Project | What it does | 26.x status |
|---|---|---|
| [Crazy Chambers](./crazy%20chambers) | Bigger, more varied Trial Chambers | ✅ Updated (data pack + mod) |
| [Woodland Mansions](./woodland%20mansions) | Larger, reimagined Woodland Mansions | ✅ Updated (data pack + mod) |
| [Grand Capitals](./grand%20capitals) | Rebuilt villages & illager structures | 🚧 In progress |
| [Strongholds](./strongholds) | Bigger, more dangerous Strongholds | 🚧 In progress |

Each project folder contains the data pack (`.zip`), the loader mod (`.jar`, for Fabric / Forge / NeoForge / Quilt), and a `modrinth-description.md` used as the store page text.

## How these work

Each mod `.jar` is a Modrinth-style **data-pack-in-a-jar wrapper**: the same data pack payload plus loader metadata (`fabric.mod.json`, `quilt.mod.json`, `META-INF/mods.toml`, `META-INF/neoforge.mods.toml`) so mod loaders can load the data pack without dropping it into a world's `datapacks/` folder. There is no compiled code — Minecraft version compatibility is governed by the `pack_format` block in `pack.mcmeta`. Use the `.zip` for a vanilla world data pack, or the `.jar` on a modded (Fabric/Forge/NeoForge/Quilt) client/server.

## License

Original works © [lukidonu](https://modrinth.com/user/lukidonu), released as *All Rights Reserved*. These re-releases are published for the community under the same terms and will be removed or transferred at the original author's request.
