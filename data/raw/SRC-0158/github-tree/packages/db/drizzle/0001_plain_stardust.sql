CREATE TYPE "public"."asset_kind" AS ENUM('pdf', 'markdown', 'image', 'video');--> statement-breakpoint
CREATE TYPE "public"."difficulty" AS ENUM('foundation', 'advanced', 'applied');--> statement-breakpoint
CREATE TYPE "public"."edge_type" AS ENUM('uses', 'integrates-with', 'secures', 'observes', 'stores', 'computes', 'delivers', 'orchestrates');--> statement-breakpoint
CREATE TABLE "cert_resource_relevance" (
	"resource_slug" text NOT NULL,
	"certification_code" "certification_code" NOT NULL,
	"domain_code" text NOT NULL,
	CONSTRAINT "cert_relevance_pk" PRIMARY KEY("resource_slug","certification_code","domain_code")
);
--> statement-breakpoint
CREATE TABLE "child_features" (
	"slug" text PRIMARY KEY NOT NULL,
	"parent_slug" text NOT NULL,
	"title" text NOT NULL,
	"summary" text NOT NULL,
	"order" integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE "content_assets" (
	"id" text PRIMARY KEY NOT NULL,
	"resource_slug" text NOT NULL,
	"kind" "asset_kind" NOT NULL,
	"access" "content_access" NOT NULL,
	"title" text NOT NULL,
	"checksum" text NOT NULL,
	"source_identity" text NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "resource_aliases" (
	"alias" text PRIMARY KEY NOT NULL,
	"canonical_slug" text NOT NULL
);
--> statement-breakpoint
CREATE TABLE "resource_edges" (
	"from_slug" text NOT NULL,
	"to_slug" text NOT NULL,
	"edge_type" "edge_type" NOT NULL,
	CONSTRAINT "resource_edges_from_slug_to_slug_edge_type_pk" PRIMARY KEY("from_slug","to_slug","edge_type")
);
--> statement-breakpoint
CREATE TABLE "resources" (
	"slug" text PRIMARY KEY NOT NULL,
	"title" text NOT NULL,
	"summary" text NOT NULL,
	"difficulty" "difficulty" NOT NULL,
	"order" integer NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "cert_resource_relevance" ADD CONSTRAINT "cert_resource_relevance_resource_slug_resources_slug_fk" FOREIGN KEY ("resource_slug") REFERENCES "public"."resources"("slug") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "child_features" ADD CONSTRAINT "child_features_parent_slug_resources_slug_fk" FOREIGN KEY ("parent_slug") REFERENCES "public"."resources"("slug") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "content_assets" ADD CONSTRAINT "content_assets_resource_slug_resources_slug_fk" FOREIGN KEY ("resource_slug") REFERENCES "public"."resources"("slug") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "resource_aliases" ADD CONSTRAINT "resource_aliases_canonical_slug_resources_slug_fk" FOREIGN KEY ("canonical_slug") REFERENCES "public"."resources"("slug") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "resource_edges" ADD CONSTRAINT "resource_edges_from_slug_resources_slug_fk" FOREIGN KEY ("from_slug") REFERENCES "public"."resources"("slug") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "resource_edges" ADD CONSTRAINT "resource_edges_to_slug_resources_slug_fk" FOREIGN KEY ("to_slug") REFERENCES "public"."resources"("slug") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "cert_relevance_cert_idx" ON "cert_resource_relevance" USING btree ("certification_code");--> statement-breakpoint
CREATE INDEX "child_features_parent_idx" ON "child_features" USING btree ("parent_slug","order");--> statement-breakpoint
CREATE INDEX "content_assets_resource_idx" ON "content_assets" USING btree ("resource_slug");--> statement-breakpoint
CREATE UNIQUE INDEX "content_assets_checksum_uidx" ON "content_assets" USING btree ("checksum");--> statement-breakpoint
CREATE INDEX "resource_edges_to_idx" ON "resource_edges" USING btree ("to_slug");--> statement-breakpoint
CREATE INDEX "resource_edges_type_idx" ON "resource_edges" USING btree ("edge_type");--> statement-breakpoint
CREATE INDEX "resources_difficulty_order_idx" ON "resources" USING btree ("difficulty","order");