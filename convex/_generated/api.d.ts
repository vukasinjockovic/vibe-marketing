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
import type * as dist__generated_api from "../dist/_generated/api.js";
import type * as dist__generated_server from "../dist/_generated/server.js";
import type * as dist_activities from "../dist/activities.js";
import type * as dist_admin from "../dist/admin.js";
import type * as dist_agents from "../dist/agents.js";
import type * as dist_analytics from "../dist/analytics.js";
import type * as dist_auth from "../dist/auth.js";
import type * as dist_campaigns from "../dist/campaigns.js";
import type * as dist_documents from "../dist/documents.js";
import type * as dist_focusGroupStaging from "../dist/focusGroupStaging.js";
import type * as dist_focusGroups from "../dist/focusGroups.js";
import type * as dist_messages from "../dist/messages.js";
import type * as dist_notifications from "../dist/notifications.js";
import type * as dist_pipeline from "../dist/pipeline.js";
import type * as dist_pipelines from "../dist/pipelines.js";
import type * as dist_products from "../dist/products.js";
import type * as dist_projects from "../dist/projects.js";
import type * as dist_revisions from "../dist/revisions.js";
import type * as dist_seed from "../dist/seed.js";
import type * as dist_services from "../dist/services.js";
import type * as dist_tasks from "../dist/tasks.js";
import type * as documents from "../documents.js";
import type * as focusGroupStaging from "../focusGroupStaging.js";
import type * as focusGroups from "../focusGroups.js";
import type * as messages from "../messages.js";
import type * as notifications from "../notifications.js";
import type * as pipeline from "../pipeline.js";
import type * as pipelines from "../pipelines.js";
import type * as products from "../products.js";
import type * as projects from "../projects.js";
import type * as revisions from "../revisions.js";
import type * as seed from "../seed.js";
import type * as services from "../services.js";
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
  "dist/_generated/api": typeof dist__generated_api;
  "dist/_generated/server": typeof dist__generated_server;
  "dist/activities": typeof dist_activities;
  "dist/admin": typeof dist_admin;
  "dist/agents": typeof dist_agents;
  "dist/analytics": typeof dist_analytics;
  "dist/auth": typeof dist_auth;
  "dist/campaigns": typeof dist_campaigns;
  "dist/documents": typeof dist_documents;
  "dist/focusGroupStaging": typeof dist_focusGroupStaging;
  "dist/focusGroups": typeof dist_focusGroups;
  "dist/messages": typeof dist_messages;
  "dist/notifications": typeof dist_notifications;
  "dist/pipeline": typeof dist_pipeline;
  "dist/pipelines": typeof dist_pipelines;
  "dist/products": typeof dist_products;
  "dist/projects": typeof dist_projects;
  "dist/revisions": typeof dist_revisions;
  "dist/seed": typeof dist_seed;
  "dist/services": typeof dist_services;
  "dist/tasks": typeof dist_tasks;
  documents: typeof documents;
  focusGroupStaging: typeof focusGroupStaging;
  focusGroups: typeof focusGroups;
  messages: typeof messages;
  notifications: typeof notifications;
  pipeline: typeof pipeline;
  pipelines: typeof pipelines;
  products: typeof products;
  projects: typeof projects;
  revisions: typeof revisions;
  seed: typeof seed;
  services: typeof services;
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
