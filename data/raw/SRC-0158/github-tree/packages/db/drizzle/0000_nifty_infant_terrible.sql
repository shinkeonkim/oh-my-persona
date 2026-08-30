CREATE TYPE "public"."bookmark_type" AS ENUM('question', 'study-note');--> statement-breakpoint
CREATE TYPE "public"."certification_code" AS ENUM('aif', 'clf', 'saa');--> statement-breakpoint
CREATE TYPE "public"."content_access" AS ENUM('public', 'protected');--> statement-breakpoint
CREATE TYPE "public"."user_role" AS ENUM('pending', 'reader', 'admin');--> statement-breakpoint
CREATE TABLE "categories" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"certification_code" "certification_code" NOT NULL,
	"slug" text NOT NULL,
	"order" integer NOT NULL,
	"title" text NOT NULL,
	"summary" text DEFAULT '' NOT NULL
);
--> statement-breakpoint
CREATE TABLE "questions" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"source_id" text NOT NULL,
	"certification_code" "certification_code" NOT NULL,
	"category_slug" text NOT NULL,
	"prompt" text NOT NULL,
	"options" jsonb NOT NULL,
	"answers" jsonb NOT NULL,
	"explanation" text NOT NULL,
	"access" "content_access" DEFAULT 'protected' NOT NULL,
	CONSTRAINT "questions_source_id_unique" UNIQUE("source_id")
);
--> statement-breakpoint
CREATE TABLE "study_notes" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"certification_code" "certification_code" NOT NULL,
	"category_slug" text NOT NULL,
	"slug" text NOT NULL,
	"title" text NOT NULL,
	"markdown" text NOT NULL,
	"access" "content_access" NOT NULL
);
--> statement-breakpoint
CREATE TABLE "users" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"email" text NOT NULL,
	"display_name" text NOT NULL,
	"password_hash" text NOT NULL,
	"role" "user_role" DEFAULT 'pending' NOT NULL,
	"enabled" boolean DEFAULT true NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "users_email_unique" UNIQUE("email")
);
--> statement-breakpoint
CREATE TABLE "bookmarks" (
	"user_id" uuid NOT NULL,
	"content_type" "bookmark_type" NOT NULL,
	"content_id" uuid NOT NULL,
	"certification_code" "certification_code" NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "bookmarks_user_id_content_type_content_id_pk" PRIMARY KEY("user_id","content_type","content_id")
);
--> statement-breakpoint
CREATE TABLE "question_progress" (
	"user_id" uuid NOT NULL,
	"question_id" uuid NOT NULL,
	"attempts" integer DEFAULT 0 NOT NULL,
	"correct_attempts" integer DEFAULT 0 NOT NULL,
	"last_correct" boolean DEFAULT false NOT NULL,
	"selected_answers" jsonb NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "question_progress_user_id_question_id_pk" PRIMARY KEY("user_id","question_id")
);
--> statement-breakpoint
ALTER TABLE "bookmarks" ADD CONSTRAINT "bookmarks_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "question_progress" ADD CONSTRAINT "question_progress_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE UNIQUE INDEX "categories_cert_slug_uidx" ON "categories" USING btree ("certification_code","slug");--> statement-breakpoint
CREATE INDEX "categories_cert_order_idx" ON "categories" USING btree ("certification_code","order");--> statement-breakpoint
CREATE INDEX "questions_category_idx" ON "questions" USING btree ("certification_code","category_slug");--> statement-breakpoint
CREATE UNIQUE INDEX "study_notes_cert_slug_uidx" ON "study_notes" USING btree ("certification_code","slug");--> statement-breakpoint
CREATE INDEX "study_notes_category_idx" ON "study_notes" USING btree ("certification_code","category_slug");--> statement-breakpoint
CREATE INDEX "users_role_idx" ON "users" USING btree ("role");--> statement-breakpoint
CREATE INDEX "bookmarks_user_idx" ON "bookmarks" USING btree ("user_id","created_at");--> statement-breakpoint
CREATE INDEX "question_progress_user_idx" ON "question_progress" USING btree ("user_id","updated_at");