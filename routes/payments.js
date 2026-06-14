const express = require("express");
const router = express.Router();

const PACKS = {
  pack1: { price: "1.00", games: 1, label: "1 Partida" },
  pack3: { price: "2.50", games: 3, label: "Pack 3 Partidas" },
  pack10: { price: "7.00", games: 10, label: "Pack 10 Partidas" },
};

router.post("/create-order", async (req, res) => {
  try {
    const { packId, userId } = req.body;
    const pack = PACKS[packId] || PACKS.pack3;

    const orderId = "ORDER-" + Date.now() + "-" + Math.random().toString(36).substr(2, 9);

    res.json({
      orderId,
      pack: pack.label,
      price: pack.price,
      games: pack.games,
    });
  } catch (err) {
    console.error("Create-order error:", err);
    res.status(500).json({ error: "Failed to create order" });
  }
});

router.post("/confirm-payment", async (req, res) => {
  try {
    const { orderId, amountPaid, gamesToAdd, userId } = req.body;

    console.log(`Payment confirmed: order=${orderId}, amount=${amountPaid}, games=${gamesToAdd}, user=${userId}`);

    if (userId) {
      const sb = require("../services/supabase").getSupabase();
      const { data: profile } = await sb
        .from("profiles")
        .select("games_available")
        .eq("id", userId)
        .single();

      const currentGames = profile ? profile.games_available : 0;
      await sb
        .from("profiles")
        .update({ games_available: currentGames + gamesToAdd })
        .eq("id", userId);
    }

    res.json({ success: true });
  } catch (err) {
    console.error("Confirm-payment error:", err);
    res.status(500).json({ error: "Failed to confirm payment" });
  }
});

module.exports = router;
