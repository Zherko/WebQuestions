const express = require("express");
const router = express.Router();
const { getSupabase } = require("../services/supabase");

router.post("/paypal", async (req, res) => {
  try {
    const event = req.body;

    if (event.event_type !== "PAYMENT.CAPTURE.COMPLETED") {
      return res.status(200).send("Ignored");
    }

    const resource = event.resource;
    const customId = resource.custom_id;

    if (!customId) return res.status(200).send("No custom_id");

    const metadata = JSON.parse(customId);
    const games = metadata.games || 3;
    const userId = metadata.userId;

    if (!userId) return res.status(200).send("No userId in metadata");

    const sb = getSupabase();

    const { data: profile } = await sb
      .from("profiles")
      .select("games_available")
      .eq("id", userId)
      .single();

    const currentGames = profile ? profile.games_available : 0;

    await sb
      .from("profiles")
      .update({ games_available: currentGames + games })
      .eq("id", userId);

    console.log(`Credited ${games} games to user ${userId}`);
    res.status(200).send("OK");
  } catch (err) {
    console.error("Webhook error:", err);
    res.status(500).send("Error");
  }
});

module.exports = router;
