# Minecraft Refresh Collection

Improved & optimised derivatives of abandoned Minecraft data packs & mods, reworked for current versions of Minecraft.

Every project here started as a data pack by **[lukidonu](https://modrinth.com/user/lukidonu)**, who has [discontinued all of their projects](https://www.curseforge.com/members/lukidon/projects) (*"Projects are discontinued #RIP"*). I tried to contact the author without success. Across several updates these have been substantially reworked — bug fixes, new features and optimisation — to the point that they now carry more added code than the originals, so they're best described as improved derivatives rather than straight re-releases.

> **Based on originals by:** [lukidonu](https://modrinth.com/user/lukidonu) &nbsp;•&nbsp; **Reworked & extended by:** [darkstarworks](https://modrinth.com/user/darkstarworks)
>
> **Are you lukidonu?** Please reach out — darkstarworks@gmail.com. Happy to hand a project back or take it down on request.

## Projects

| Project | What it does | 26.x status |
|---|---|---|
| [Crazy Chambers](./crazy%20chambers) | Bigger, more varied Trial Chambers | ✅ Updated (data pack + mod) |
| [Woodland Mansions](./woodland%20mansions) | Larger, reimagined Woodland Mansions | ✅ Updated (data pack + mod) |
| [Grand Capitals](./grand%20capitals) | Rebuilt villages & illager structures | ✅ Updated (data pack + mod) |
| [Strongholds](./strongholds) | Bigger, more dangerous Strongholds | ✅ Updated (data pack + mod) |
| [Ancient Cities](./ancient%20cities) | New Ancient Cities to be lost in | ✅ Updated (data pack + mod) |

Each project folder contains the data pack (`.zip`), the loader mod (`.jar`, for Fabric / Forge / NeoForge / Quilt), and a `modrinth-description.md` used as the store page text.

## How these work

Each mod `.jar` is a Modrinth-style **data-pack-in-a-jar wrapper**: the same data pack payload plus loader metadata (`fabric.mod.json`, `quilt.mod.json`, `META-INF/mods.toml`, `META-INF/neoforge.mods.toml`) so mod loaders can load the data pack without dropping it into a world's `datapacks/` folder. There is no compiled code — Minecraft version compatibility is governed by the `pack_format` block in `pack.mcmeta`. Use the `.zip` for a vanilla world data pack, or the `.jar` on a modded (Fabric/Forge/NeoForge/Quilt) client/server.

## Customise the loot

Every chest, barrel, pot and reward vault in these packs can be tuned without touching any JSON. Each pack has a plain-text settings file in [`loot/`](./loot) where you set how common each item is (`rarity`), how many drop (`amount`), and how full each container rolls (`draws`) — you can add or remove items too. Double-click **`Build-Loot.exe`** and it validates your changes (misspelled item names are caught before anything is written), then patches every pack's `.zip` **and** `.jar` in sync. On Linux/Mac, run [`tools/build_loot.py`](./tools/build_loot.py) instead — it's identical. Full guide: [`loot/HOW TO CHANGE LOOT.txt`](./loot/HOW%20TO%20CHANGE%20LOOT.txt).

## License

Based on original works © [lukidonu](https://modrinth.com/user/lukidonu), released as *All Rights Reserved*; modifications and added code © [darkstarworks](https://modrinth.com/user/darkstarworks). These derivatives are published for the community under the same terms and will be removed or transferred at the original author's request.
