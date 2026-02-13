/* eslint-disable */
/**
 * Generated `api` utility.
 *
 * THIS CODE IS AUTOMATICALLY GENERATED.
 *
 * To regenerate, run `npx convex dev`.
 * @module
 */

import type * as activities from "../activities.js";
import type * as admin from "../admin.js";
import type * as agents from "../agents.js";
import type * as analytics from "../analytics.js";
import type * as auth from "../auth.js";
import type * as campaigns from "../campaigns.js";
import type * as documents from "../documents.js";
import type * as focusGroupStaging from "../focusGroupStaging.js";
import type * as focusGroups from "../focusGroups.js";
import type * as messages from "../messages.js";
import type * as notifications from "../notifications.js";
import type * as orchestrator from "../orchestrator.js";
import type * as pipeline from "../pipeline.js";
import type * as pipelines from "../pipelines.js";
import type * as products from "../products.js";
import type * as projects from "../projects.js";
import type * as revisions from "../revisions.js";
import type * as seed from "../seed.js";
import type * as services from "../services.js";
import type * as skillCategories from "../skillCategories.js";
import type * as skills from "../skills.js";
import type * as tasks from "../tasks.js";

import type {
  ApiFromModules,
  FilterApi,
  FunctionReference,
} from "convex/server";

declare const fullApi: ApiFromModules<{
  activities: typeof activities;
  admin: typeof admin;
  agents: typeof agents;
  analytics: typeof analytics;
  auth: typeof auth;
  campaigns: typeof campaigns;
  documents: typeof documents;
  focusGroupStaging: typeof focusGroupStaging;
  focusGroups: typeof focusGroups;
  messages: typeof messages;
  notifications: typeof notifications;
  orchestrator: typeof orchestrator;
  pipeline: typeof pipeline;
  pipelines: typeof pipelines;
  products: typeof products;
  projects: typeof projects;
  revisions: typeof revisions;
  seed: typeof seed;
  services: typeof services;
  skillCategories: typeof skillCategories;
  skills: typeof skills;
  tasks: typeof tasks;
}>;

/**
 * A utility for referencing Convex functions in your app's public API.
 *
 * Usage:
 * ```js
 * const myFunctionReference = api.myModule.myFunction;
 * ```
 */
export declare const api: FilterApi<
  typeof fullApi,
  FunctionReference<any, "public">
>;

/**
 * A utility for referencing Convex functions in your app's internal API.
 *
 * Usage:
 * ```js
 * const myFunctionReference = internal.myModule.myFunction;
 * ```
 */
export declare const internal: FilterApi<
  typeof fullApi,
  FunctionReference<any, "internal">
>;

export declare const components: {};
