import { internalAction, internalMutation } from "./_generated/server";
import { v } from "convex/values";
import { internal } from "./_generated/api";

// Internal action: hash password with bcrypt (runs in Node.js runtime)
export const createUser = internalAction({
  args: {
    email: v.string(),
    name: v.string(),
    password: v.string(),
    role: v.union(v.literal("admin"), v.literal("editor"), v.literal("viewer")),
  },
  handler: async (ctx, args) => {
    const bcrypt = await import("bcryptjs");
    const passwordHash = await bcrypt.hash(args.password, 12);

    const userId = await ctx.runMutation(internal.admin.insertUser, {
      email: args.email,
      name: args.name,
      passwordHash,
      role: args.role,
    });

    return userId;
  },
});

// Internal mutation: insert user record
export const insertUser = internalMutation({
  args: {
    email: v.string(),
    name: v.string(),
    passwordHash: v.string(),
    role: v.union(v.literal("admin"), v.literal("editor"), v.literal("viewer")),
  },
  handler: async (ctx, args) => {
    // Check for existing user
    const existing = await ctx.db
      .query("users")
      .withIndex("by_email", (q) => q.eq("email", args.email))
      .unique();

    if (existing) {
      throw new Error(`User with email ${args.email} already exists`);
    }

    return await ctx.db.insert("users", {
      email: args.email,
      name: args.name,
      passwordHash: args.passwordHash,
      role: args.role,
      status: "active",
    });
  },
});
