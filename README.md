# Minecraft Refresh Collection

Improved & optimised derivatives of abandoned Minecraft data packs, mods & resource packs, reworked for current versions of Minecraft.

Every project here started as a data pack by **[lukidonu](https://modrinth.com/user/lukidonu)**, who has [discontinued all of their projects](https://www.curseforge.com/members/lukidon/projects) (*"Projects are discontinued #RIP"*). I tried to contact the author without success. Across several updates these have been substantially reworked — bug fixes, new features and optimisation — to the point that they now carry more added code than the originals, so they're best described as improved derivatives rather than straight re-releases.

> **Based on originals by:** [lukidonu](https://modrinth.com/user/lukidonu) &nbsp;•&nbsp; **Reworked & extended by:** [darkstarworks](https://modrinth.com/user/darkstarworks)
>
> **Are you lukidonu?** Please reach out — darkstarworks@gmail.com. Happy to hand a project back or take it down on request.

## Projects

| Project | What it does | Status |
|---|---|---|
| [Crazy Chambers](./crazy%20chambers) | Bigger, more varied Trial Chambers | ✅ 26.2 & 26.3 (data pack + mod) |
| [Woodland Mansions](./woodland%20mansions) | Larger, reimagined Woodland Mansions | ✅ 26.2 & 26.3 (data pack + mod) |
| [Grand Capitals](./grand%20capitals) | Rebuilt villages & illager structures | ✅ 26.2 & 26.3 (data pack + mod) |
| [Strongholds](./strongholds) | Bigger, more dangerous Strongholds | ✅ 26.2 & 26.3 (data pack + mod) |
| [Ancient Cities](./ancient%20cities) | New Ancient Cities to be lost in | ✅ 26.2 & 26.3 (data pack + mod) |

### Resource packs

These change how mobs look. Drop the `.zip` into your `resourcepacks` folder and turn it on in **Options > Resource Packs**.

| Project | What it does | Status |
|---|---|---|
| [Boss Refreshed](./boss%20refreshed) | New looks for the Ender Dragon, Wither, Warden & Elder Guardian | ✅ 26.2 & 26.3 |
| [Mobs Refreshed](./mobs%20refreshed) | New looks for the hostile mobs | ✅ 26.2 & 26.3 |

Each resource pack also carries optional model files for reshaped mob bodies. Plain Minecraft ignores them, so the new pictures work either way; the reshaped bodies need **OptiFine**, or **Entity Model Features (EMF)** on Fabric.

Each data pack folder contains the data pack (`.zip`), the loader mod (`.jar`, for Fabric / Forge / NeoForge / Quilt), and a `modrinth-description.md` used as the store page text. Resource pack folders hold just the `.zip` and their description.

## One download, two Minecraft versions

Every pack works on both **26.2** and **26.3** from the same file. 26.3 changed the way several things are written, so each pack carries a small extra folder with the 26.3 wording; Minecraft picks whichever set matches the version you are running and ignores the other. You do not have to choose a download.

## How these work

Each mod `.jar` is a Modrinth-style **data-pack-in-a-jar wrapper**: the same data pack payload plus loader metadata (`fabric.mod.json`, `quilt.mod.json`, `META-INF/mods.toml`, `META-INF/neoforge.mods.toml`) so mod loaders can load the data pack without dropping it into a world's `datapacks/` folder. There is no compiled code — Minecraft version compatibility is governed by the `min_format` / `max_format` block in `pack.mcmeta`. Use the `.zip` for a vanilla world data pack, or the `.jar` on a modded (Fabric/Forge/NeoForge/Quilt) client/server.

## Building from source

The editable files live in [`src/`](./src), one folder per pack. Run `python3 tools/build_pack.py` to turn them back into the `.zip` and `.jar` you see in each project folder. The 26.3 folder inside each pack is generated automatically by `tools/convert_26_3.py`, so only the main files are ever edited by hand.

## Customise the loot

Every chest, barrel, pot and reward vault in these packs can be tuned without touching any JSON. Each pack has a plain-text settings file in [`loot/`](./loot) where you set how common each item is (`rarity`), how many drop (`amount`), and how full each container rolls (`draws`) — you can add or remove items too. Double-click **`Build-Loot.exe`** and it validates your changes (misspelled item names are caught before anything is written), then rebuilds every pack's `.zip` **and** `.jar` in sync. On Linux/Mac, run [`tools/build_loot.py`](./tools/build_loot.py) instead — it's identical. Full guide: [`loot/HOW TO CHANGE LOOT.txt`](./loot/HOW%20TO%20CHANGE%20LOOT.txt).

## License

Based on original works © [lukidonu](https://modrinth.com/user/lukidonu), released as *All Rights Reserved*; modifications and added code © [darkstarworks](https://modrinth.com/user/darkstarworks). These derivatives are published for the community under the same terms and will be removed or transferred at the original author's request.
