CREATE TYPE "public"."source_artifact_kind" AS ENUM('study-note', 'concept-note', 'resource-section', 'linked-pdf', 'root-pdf');--> statement-breakpoint
CREATE TABLE "source_artifacts" (
	"id" text PRIMARY KEY NOT NULL,
	"source_namespace" text NOT NULL,
	"certification_code" "certification_code" NOT NULL,
	"kind" "source_artifact_kind" NOT NULL,
	"access" "content_access" NOT NULL,
	"title" text NOT NULL,
	"markdown" text,
	"checksum" text NOT NULL,
	"source_identity" text NOT NULL,
	"parent_id" text,
	"order" integer NOT NULL
);
--> statement-breakpoint
CREATE INDEX "source_artifacts_namespace_kind_idx" ON "source_artifacts" USING btree ("source_namespace","kind");--> statement-breakpoint
CREATE INDEX "source_artifacts_cert_order_idx" ON "source_artifacts" USING btree ("certification_code","kind","order");--> statement-breakpoint
CREATE INDEX "source_artifacts_identity_idx" ON "source_artifacts" USING btree ("source_namespace","source_identity");